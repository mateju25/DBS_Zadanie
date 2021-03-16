# Generated by Django 3.1.6 on 2021-03-16 16:51

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("""DROP TABLE IF EXISTS ov.companies;
                                        CREATE TABLE ov.companies (
                                            cin         bigint PRIMARY KEY,
                                            name        character varying(255),
                                            br_section  character varying(255),
                                            adress_line character varying(255),
                                            last_update timestamp without time zone,
                                            created_at  timestamp without time zone,
                                            updated_at timestamp without time zone
                                        );
                                        --podanie
                                        INSERT INTO ov.companies(cin, name, br_section, adress_line, last_update, created_at, updated_at)
                                        SELECT cin, corporate_body_name, br_section, address_line, updated_at, now(), now()
                                        FROM
                                        (
                                             SELECT cin, corporate_body_name, br_section, address_line, updated_at, (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
                                             FROM ov.or_podanie_issues WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.or_podanie_issues.cin)
                                        ) X 
                                        WHERE row_n = 1;
                                        --likvidator
                                        INSERT INTO ov.companies(cin, name, br_section, adress_line, last_update, created_at, updated_at)
                                        SELECT cin, corporate_body_name, br_section, adress_line, updated_at, now(), now()
                                        FROM
                                        (
                                             SELECT cin, corporate_body_name, br_section, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
                                             FROM ov.likvidator_issues WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.likvidator_issues.cin)
                                        ) X 
                                        WHERE row_n = 1;
                                        --konkurz_vyrovnanie_issues
                                        INSERT INTO ov.companies(cin, name, br_section, adress_line, last_update, created_at, updated_at)
                                        SELECT cin, corporate_body_name, null, adress_line, updated_at, now(), now()
                                        FROM
                                        (
                                             SELECT cin, corporate_body_name, null, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
                                             FROM ov.konkurz_vyrovnanie_issues WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.konkurz_vyrovnanie_issues.cin)
                                        ) X 
                                        WHERE row_n = 1;
                                        --znizenie_imania_issues
                                        INSERT INTO ov.companies(cin, name, br_section, adress_line, last_update, created_at, updated_at)
                                        SELECT cin, corporate_body_name, br_section, adress_line, updated_at, now(), now()
                                        FROM
                                        (
                                             SELECT cin, corporate_body_name, br_section, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
                                             FROM ov.znizenie_imania_issues WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.znizenie_imania_issues.cin)
                                        ) X 
                                        WHERE row_n = 1;

                                        --konkurz_restrukturalizacia_actors
                                        INSERT INTO ov.companies(cin, name, br_section, adress_line, last_update, created_at, updated_at)
                                        SELECT cin, corporate_body_name, null, adress_line, updated_at, now(), now()
                                        FROM
                                        (
                                             SELECT cin, corporate_body_name, null, CONCAT(street, ', ', postal_code, city) AS adress_line, updated_at, (row_number() OVER (PARTITION BY cin ORDER BY updated_at DESC)) AS row_n
                                             FROM ov.konkurz_restrukturalizacia_actors WHERE cin IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ov.companies comp WHERE comp.cin = ov.konkurz_restrukturalizacia_actors.cin)
                                        ) X 
                                        WHERE row_n = 1;""")
    ]