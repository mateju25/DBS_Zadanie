# Generated by Django 3.1.6 on 2021-03-16 16:51

from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("""
        CREATE TABLE IF NOT EXISTS ov.companies (
            cin         bigint PRIMARY KEY,
            name        character varying(255),
            br_section  character varying(255),
            address_line character varying(255),
            last_update timestamp without time zone,
            created_at  timestamp without time zone,
            updated_at timestamp without time zone
        );"""),
        migrations.RunSQL("""
        --podanie
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT cin, corporate_body_name, br_section, address_line, updated_at, now(), now()
        FROM
        (
             SELECT cin, corporate_body_name, br_section, address_line, updated_at, 
                    (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
             FROM ov.or_podanie_issues 
                WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.or_podanie_issues.cin)
        ) X 
        WHERE row_n = 1;"""),
        migrations.RunSQL("""
        --likvidator
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT cin, corporate_body_name, br_section, adress_line, updated_at, now(), now()
        FROM
        (
             SELECT cin, corporate_body_name, br_section, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, 
                (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
             FROM ov.likvidator_issues 
                WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.likvidator_issues.cin)
        ) X 
        WHERE row_n = 1;"""),
        migrations.RunSQL("""
        --konkurz_vyrovnanie_issues
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT cin, corporate_body_name, null, adress_line, updated_at, now(), now()
        FROM
        (
             SELECT cin, corporate_body_name, null, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, 
                (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
             FROM ov.konkurz_vyrovnanie_issues 
                WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.konkurz_vyrovnanie_issues.cin)
        ) X 
        WHERE row_n = 1;"""),
        migrations.RunSQL("""
        --znizenie_imania_issues
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT cin, corporate_body_name, br_section, adress_line, updated_at, now(), now()
        FROM
        (
             SELECT cin, corporate_body_name, br_section, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, 
                (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
             FROM ov.znizenie_imania_issues 
                WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.znizenie_imania_issues.cin)
        ) X 
        WHERE row_n = 1;"""),
        migrations.RunSQL("""
        --konkurz_restrukturalizacia_actors
        INSERT INTO ov.companies(cin, name, br_section, address_line, last_update, created_at, updated_at)
        SELECT cin, corporate_body_name, null, adress_line, updated_at, now(), now()
        FROM
        (
             SELECT cin, corporate_body_name, null, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, 
                (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
             FROM ov.konkurz_restrukturalizacia_actors 
                WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.konkurz_restrukturalizacia_actors.cin)
        ) X 
        WHERE row_n = 1;"""),
        migrations.RunSQL("""
        --dopln stlpce do ostatnych tabuliek a napln ich hodnotami
        ALTER TABLE ov.or_podanie_issues
        ADD COLUMN IF NOT EXISTS company_id bigint REFERENCES ov.companies(cin); 
        ALTER TABLE ov.likvidator_issues
        ADD COLUMN IF NOT EXISTS company_id bigint REFERENCES ov.companies(cin); 
        ALTER TABLE ov.konkurz_vyrovnanie_issues
        ADD COLUMN IF NOT EXISTS company_id bigint REFERENCES ov.companies(cin); 
        ALTER TABLE ov.znizenie_imania_issues
        ADD COLUMN IF NOT EXISTS company_id bigint REFERENCES ov.companies(cin); 
        ALTER TABLE ov.konkurz_restrukturalizacia_actors
        ADD COLUMN IF NOT EXISTS company_id bigint REFERENCES ov.companies(cin); """),
        migrations.RunSQL("""
        UPDATE ov.or_podanie_issues
        SET company_id = cin WHERE cin IS NOT null;"""),
        migrations.RunSQL("""
        UPDATE ov.likvidator_issues
        SET company_id = cin WHERE cin IS NOT null;"""),
        migrations.RunSQL("""
        UPDATE ov.konkurz_vyrovnanie_issues
        SET company_id = cin WHERE cin IS NOT null;"""),
        migrations.RunSQL("""
        UPDATE ov.znizenie_imania_issues
        SET company_id = cin WHERE cin IS NOT null;"""),
        migrations.RunSQL("""
        UPDATE ov.konkurz_restrukturalizacia_actors
        SET company_id = cin WHERE cin IS NOT null;""")
    ]
