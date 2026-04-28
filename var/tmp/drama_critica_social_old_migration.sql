-- Safe migration for category 019d7dbe-bea3-73a6-8abf-ad65f1367c90
-- Blocker intentionally excluded: A Filha do Barão (019d91fa-53bd-7069-89ec-bbc2316aadbe)

UPDATE "Books"
SET "CategoryId" = '123dfbc8-3c1a-43a3-8dc3-30d1409662a4'
WHERE "CategoryId" = '019d7dbe-bea3-73a6-8abf-ad65f1367c90'
  AND "Id" IN (
    '019d404d-4774-73d1-81bf-65d75242c4cb', -- A Cidade e as Serras
    '019d2b1f-89d9-7b1a-b5e5-44b9aa0d84d1', -- A Ilustre Casa de Ramires
    '019d7fa3-f1bf-7fd0-82dc-c1620cdacd08', -- A Revolucao dos Bichos
    '019da438-14d4-7eb6-8c94-de7f5b413389', -- Cartas Chilenas
    '019da89d-ec1b-7f14-8522-a5af06c49585', -- Macunaíma
    '019da865-00e1-7984-b833-593156ef0086', -- Os Bruzundangas
    '019d991c-98ac-71a9-9f40-3ddc61490415', -- Teoria do Medalhão
    '019da862-0fe3-7cd2-aaf2-578d19230d15'  -- Triste Fim de Policarpo Quaresma
  );

UPDATE "Books"
SET "CategoryId" = '9f8f25f3-e078-43fa-9cab-f8b5bb583a85'
WHERE "CategoryId" = '019d7dbe-bea3-73a6-8abf-ad65f1367c90'
  AND "Id" IN (
    '2018f412-d37b-45a6-92b1-08d91ea9abfa' -- Auto da Compadecida
  );

UPDATE "Books"
SET "CategoryId" = '00a5cf45-b334-453a-96c3-76a134224f64'
WHERE "CategoryId" = '019d7dbe-bea3-73a6-8abf-ad65f1367c90'
  AND "Id" IN (
    '019d9ebf-8d5e-79e6-aa59-095cf7564de3' -- O Ateneu
  );

UPDATE "Books"
SET "CategoryId" = 'b5cdac27-d43b-4b99-96d9-285a8053e8bc'
WHERE "CategoryId" = '019d7dbe-bea3-73a6-8abf-ad65f1367c90'
  AND "Id" IN (
    '019d27e1-2022-779e-b23d-845742f287bb', -- As Vítimas-Algozes
    '019da41c-b553-7e72-9d4b-8c245ffadf5e'  -- Pai Contra Mãe
  );

UPDATE "Books"
SET "CategoryId" = '234b8d86-7aef-41bb-a620-7bca29806b2e'
WHERE "CategoryId" = '019d7dbe-bea3-73a6-8abf-ad65f1367c90'
  AND "Id" IN (
    '019d9e88-c854-747e-9b06-234cd4a8eb03', -- Clara dos Anjos
    '019d4623-4176-7258-955a-a81a7c673354', -- O Crime do Padre Amaro
    '019d45b5-3c56-7377-a979-64734d5ec441', -- Os Maias
    '019d965f-0c46-7c96-896d-31d7f64884a5'  -- Vidas Secas
  );

UPDATE "Books"
SET "CategoryId" = '3a7cedce-b30a-4742-ad96-1213e8061bd9'
WHERE "CategoryId" = '019d7dbe-bea3-73a6-8abf-ad65f1367c90'
  AND "Id" IN (
    '019d99b4-80f8-7d9e-8cab-251e101429a4', -- A Normalista
    '019d9ebf-5f68-7a3f-a639-a0ad5974d9b6', -- Casa de Pensão
    '019da3e5-c7f8-7ffb-8089-cc2712b6afa7', -- Contos
    '019d8054-e99a-7339-b410-c9b36c23920f', -- Luzia-Homem
    '019d4964-cd8c-7d45-9128-c094bc4203d9', -- O Cortiço
    '019d80d1-55b8-76d2-9816-5ca6f30aa093', -- O Moleque
    '019d99eb-965d-7672-a454-c2cc6a88e988', -- O Mulato
    '019d6f70-8a08-787d-a8f8-3b105ed43773', -- O Ventre de Nápoles
    '019d708c-4fc2-7e85-80e2-65a2c3562540', -- Oliver Twist
    '019d745b-d71a-7587-acfe-db1f57096210', -- Os Miseráveis
    '019da7fc-0e32-7fb3-a597-e5e96c159e34'  -- Úrsula e Outras Obras
  );
