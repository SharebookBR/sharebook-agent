using System.Text.Json;
using Npgsql;

var repoRoot = @"C:\REPOS\SHAREBOOK";
var appSettingsPath = Path.Combine(repoRoot, "sharebook-backend", "ShareBook", "ShareBook.Api", "appsettings.Development.json");
var appSettings = JsonDocument.Parse(await File.ReadAllTextAsync(appSettingsPath));
var connectionString = appSettings.RootElement
    .GetProperty("ConnectionStrings")
    .GetProperty("PostgresConnection")
    .GetString();

if (string.IsNullOrWhiteSpace(connectionString))
{
    throw new InvalidOperationException("Connection string ausente em appsettings.Development.json.");
}

await using var conn = new NpgsqlConnection(connectionString);
await conn.OpenAsync();

var tecnologiaId = await EnsureRootCategoryAsync(conn, "Tecnologia");
var ficcaoId = await EnsureRootCategoryAsync(conn, "Ficção");

foreach (var child in new[] { "Backend", "Frontend", "Cloud", "Dados", "IA", "DevOps" })
{
    await EnsureChildCategoryAsync(conn, tecnologiaId, child);
}

foreach (var child in new[] { "Terror", "Fantasia", "Drama" })
{
    await ReparentRootCategoryAsync(conn, ficcaoId, child);
}

foreach (var child in new[] { "Terror", "Fantasia", "Ficção científica", "Mistério / Suspense", "Aventura", "Drama" })
{
    await EnsureChildCategoryAsync(conn, ficcaoId, child);
}

var backendId = await RequireCategoryIdAsync(conn, "Backend", tecnologiaId);
var frontendId = await RequireCategoryIdAsync(conn, "Frontend", tecnologiaId);
var cloudId = await RequireCategoryIdAsync(conn, "Cloud", tecnologiaId);

var bookMoves = new (string Title, Guid CategoryId, string CategoryPath)[]
{
    ("clean code", backendId, "Tecnologia > Backend"),
    ("Programação de Redes com Python", cloudId, "Tecnologia > Cloud"),
    ("Programando o Android", frontendId, "Tecnologia > Frontend"),
    ("Programação de jogo Android", frontendId, "Tecnologia > Frontend"),
};

foreach (var move in bookMoves)
{
    await MoveBookToCategoryAsync(conn, move.Title, move.CategoryId, move.CategoryPath);
}

await PrintMovedBooksAsync(conn, bookMoves.Select(move => move.Title).ToArray());
await PrintCategoryTreeAsync(conn);

static async Task<Guid> EnsureRootCategoryAsync(NpgsqlConnection conn, string name)
{
    var existingId = await FindCategoryIdAsync(conn, name, null);
    if (existingId.HasValue)
    {
        return existingId.Value;
    }

    var id = Guid.NewGuid();
    const string sql = """
        insert into "Categories" ("Id", "Name", "CreationDate")
        values (@id, @name, now() at time zone 'utc');
        """;

    await using var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("id", id);
    cmd.Parameters.AddWithValue("name", name);
    await cmd.ExecuteNonQueryAsync();
    return id;
}

static async Task EnsureChildCategoryAsync(NpgsqlConnection conn, Guid parentId, string name)
{
    var existingId = await FindCategoryIdAsync(conn, name, parentId);
    if (existingId.HasValue)
    {
        return;
    }

    var id = Guid.NewGuid();
    const string sql = """
        insert into "Categories" ("Id", "Name", "ParentCategoryId", "CreationDate")
        values (@id, @name, @parentId, now() at time zone 'utc');
        """;

    await using var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("id", id);
    cmd.Parameters.AddWithValue("name", name);
    cmd.Parameters.AddWithValue("parentId", parentId);
    await cmd.ExecuteNonQueryAsync();
}

static async Task ReparentRootCategoryAsync(NpgsqlConnection conn, Guid parentId, string name)
{
    var rootId = await FindCategoryIdAsync(conn, name, null);
    if (!rootId.HasValue)
    {
        return;
    }

    var childId = await FindCategoryIdAsync(conn, name, parentId);
    if (childId.HasValue)
    {
        return;
    }

    const string sql = """
        update "Categories"
        set "ParentCategoryId" = @parentId
        where "Id" = @id;
        """;

    await using var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("parentId", parentId);
    cmd.Parameters.AddWithValue("id", rootId.Value);
    await cmd.ExecuteNonQueryAsync();
}

static async Task<Guid?> FindCategoryIdAsync(NpgsqlConnection conn, string name, Guid? parentId)
{
    var sql = parentId.HasValue
        ? """
          select "Id"
          from "Categories"
          where "Name" = @name
            and "ParentCategoryId" = @parentId
          limit 1;
          """
        : """
          select "Id"
          from "Categories"
          where "Name" = @name
            and "ParentCategoryId" is null
          limit 1;
          """;

    await using var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("name", name);
    if (parentId.HasValue)
    {
        cmd.Parameters.AddWithValue("parentId", parentId.Value);
    }

    var result = await cmd.ExecuteScalarAsync();
    return result is Guid id ? id : null;
}

static async Task<Guid> RequireCategoryIdAsync(NpgsqlConnection conn, string name, Guid? parentId)
{
    var categoryId = await FindCategoryIdAsync(conn, name, parentId);
    if (!categoryId.HasValue)
    {
        throw new InvalidOperationException($"Categoria não encontrada: {name}");
    }

    return categoryId.Value;
}

static async Task MoveBookToCategoryAsync(NpgsqlConnection conn, string title, Guid categoryId, string categoryPath)
{
    const string sql = """
        update "Books"
        set "CategoryId" = @categoryId
        where lower(trim("Title")) = lower(trim(@title));
        """;

    await using var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("categoryId", categoryId);
    cmd.Parameters.AddWithValue("title", title);
    var rows = await cmd.ExecuteNonQueryAsync();

    if (rows == 0)
    {
        throw new InvalidOperationException($"Livro não encontrado para mover: {title}");
    }

    Console.WriteLine($"BOOK\t{title}\t{categoryPath}");
}

static async Task PrintMovedBooksAsync(NpgsqlConnection conn, string[] titles)
{
    const string sql = """
        select b."Title", c."Name" as category_name, p."Name" as parent_name
        from "Books" b
        join "Categories" c on c."Id" = b."CategoryId"
        left join "Categories" p on p."Id" = c."ParentCategoryId"
        where lower(trim(b."Title")) = any(@titles)
        order by b."Title";
        """;

    var normalizedTitles = titles
        .Select(title => title.Trim().ToLowerInvariant())
        .ToArray();

    await using var cmd = new NpgsqlCommand(sql, conn);
    cmd.Parameters.AddWithValue("titles", normalizedTitles);

    await using var reader = await cmd.ExecuteReaderAsync();
    while (await reader.ReadAsync())
    {
        var title = reader.GetString(0);
        var categoryName = reader.GetString(1);
        var parentName = reader.IsDBNull(2) ? "" : reader.GetString(2);
        var categoryPath = string.IsNullOrWhiteSpace(parentName)
            ? categoryName
            : $"{parentName} > {categoryName}";
        Console.WriteLine($"CHECK\t{title}\t{categoryPath}");
    }
}

static async Task PrintCategoryTreeAsync(NpgsqlConnection conn)
{
    const string sql = """
        select c."Name" as child_name, p."Name" as parent_name
        from "Categories" c
        left join "Categories" p on p."Id" = c."ParentCategoryId"
        order by coalesce(p."Name", c."Name"), p."Name" nulls first, c."Name";
        """;

    await using var cmd = new NpgsqlCommand(sql, conn);
    await using var reader = await cmd.ExecuteReaderAsync();

    while (await reader.ReadAsync())
    {
        var childName = reader.GetString(0);
        var parentName = reader.IsDBNull(1) ? "" : reader.GetString(1);
        Console.WriteLine(string.IsNullOrWhiteSpace(parentName)
            ? $"ROOT\t{childName}"
            : $"CHILD\t{parentName}\t{childName}");
    }
}
