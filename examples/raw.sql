
INSERT INTO "address" (line_1, id)
VALUES
    ('Celestia', 'c5fb851f-63fd-4572-872c-3597186c9afe'),
    ('The imperial road', 'cd521f7e-df61-4079-b44d-35015b9b5110');

INSERT INTO "bank_details" (account_number, account_type, id)
VALUES
    ('payusnothing', 'cash', 'ccd390cf-a74c-4897-a923-3d77ce1b97bf');

INSERT INTO "category" (name, id)
VALUES
    ('Baked goods', '3674c73c-a967-493f-9a4b-5b70f78a5a99'),
    ('ISP', 'f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7');

INSERT INTO "supplier" (created_at, email, name, address_id, bank_details_id, id)
VALUES
    ('2020-02-21 00:00:00', 'info@loros.example', 'Loros Grist', 'c5fb851f-63fd-4572-872c-3597186c9afe', 'ccd390cf-a74c-4897-a923-3d77ce1b97bf', '2b7e7211-d2c7-4eb4-8c14-05ed58c77473');

INSERT INTO "supplier_category" (supplier_id, category_id, id)
VALUES
    ('2b7e7211-d2c7-4eb4-8c14-05ed58c77473', 'f66c3eb7-7b93-4d9f-bc66-8ff07353f5e7', 'da2add70-7284-4966-983b-33281c149e65'),
    ('2b7e7211-d2c7-4eb4-8c14-05ed58c77473', '3674c73c-a967-493f-9a4b-5b70f78a5a99', 'e1986144-26b7-4d1a-a8c6-5f9be9a52039');

INSERT INTO "contact" (name, email, address_id, supplier_id, id)
VALUES
    ('Sveimann Glort', 'sveimann@loros.example', 'cd521f7e-df61-4079-b44d-35015b9b5110', '2b7e7211-d2c7-4eb4-8c14-05ed58c77473', '98a11210-949a-48ad-99c7-1d89c54c2a53');
