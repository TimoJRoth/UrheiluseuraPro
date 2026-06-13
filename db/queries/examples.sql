-- UrheiluseuraPro – kaikki vaaditut haut (v1.1.0)
-- Kaksi strategiaa:
--   A) organization_profile (nopein, 100k+ org) – suositeltu listauksiin
--   B) child-taulu JOIN (totuuden lähde, monipaikkaiset org:t)

-- =============================================================================
-- A) NOPEAT HAUT – organization_profile
-- =============================================================================

-- 1. Kaikki seurat
SELECT o.id, pn.name, p.*
FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 2. Tietyn lajin seurat (esim. jääkiekko)
SELECT o.id, pn.name
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_sports os ON os.organization_id = o.id
JOIN sports s ON s.id = os.sport_id
WHERE s.slug = 'jaakiekko';
-- slug: salibandy | jalkapallo | golf | voimistelu

-- 3. Tietyn kaupungin seurat (Tampere = 837)
SELECT o.id, pn.name
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_profile p ON p.organization_id = o.id
WHERE p.primary_municipality_code = '837';

-- 4. Tietyn maakunnan seurat (Pirkanmaa = 11)
SELECT o.id, pn.name
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_profile p ON p.organization_id = o.id
WHERE p.primary_region_code = '11';

-- 5. Monilajiseurat
SELECT o.id, pn.name, p.sport_count
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_profile p ON p.organization_id = o.id
WHERE p.is_multi_sport = 1;

-- 6. Seurat joilla on sähköposti
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_email = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 7. Seurat joilla on verkkosivut
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_website = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 8. Seurat joilla on Facebook
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_facebook = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 9. Seurat joilla on Instagram
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_instagram = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 10. Seurat joilla on LinkedIn
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_linkedin = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 11. Seurat joilla on yhteyshenkilö
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_contact_person = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 12. Seurat joilla on puhelinnumero
SELECT o.id, pn.name FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_phone = 1
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- =============================================================================
-- B) TOTUUDEN LÄHDE – child-taulut (monipaikkaiset / monilajiset)
-- =============================================================================

-- Kaikki Pirkanmaan seurat (mikä tahansa toimipaikka maakunnassa)
SELECT DISTINCT o.id, pn.name
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_locations ol ON ol.organization_id = o.id
JOIN municipalities m ON m.code = ol.municipality_code
WHERE m.region_code = '11';

-- Kaikki Tampereen seurat (mikä tahansa toimipaikka kunnassa)
SELECT DISTINCT o.id, pn.name
FROM organizations o
JOIN organization_locations ol ON ol.organization_id = o.id
WHERE ol.municipality_code = '837';

-- Monilajiseurat (lasketaan riveistä, ei profiilista)
SELECT o.id, pn.name, COUNT(os.sport_id) AS sport_count
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_sports os ON os.organization_id = o.id
GROUP BY o.id
HAVING COUNT(os.sport_id) > 1;

-- Facebook (kaikki tilit, ei vain lippu)
SELECT o.id, pn.name, osa.account_url
FROM organizations o
JOIN organization_social_accounts osa ON osa.organization_id = o.id
WHERE osa.platform = 'facebook';

-- =============================================================================
-- 13. Seurat joilla on jäsenmäärätiedot
SELECT o.id, pn.name, sz.member_count, sz.junior_member_count, sz.adult_member_count
FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id AND p.has_member_count = 1
JOIN organization_size sz ON sz.organization_id = o.id
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 14. Seurat joilla on kotikenttä
SELECT o.id, pn.name, ol.name AS home_field, ol.latitude, ol.longitude
FROM organizations o
JOIN organization_activity oa ON oa.organization_id = o.id
JOIN organization_locations ol ON ol.id = oa.home_field_location_id
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 15. Seurat joilla on kotihalli
SELECT o.id, pn.name, ol.name AS home_hall
FROM organizations o
JOIN organization_activity oa ON oa.organization_id = o.id
JOIN organization_locations ol ON ol.id = oa.home_hall_location_id
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 16. Seurat joilla on harjoituspaikkoja
SELECT o.id, pn.name, tf.name AS training_facility
FROM organizations o
JOIN organization_training_facilities tf ON tf.organization_id = o.id
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- 17. Koordinaattihaku (primary location)
SELECT o.id, pn.name, p.primary_latitude, p.primary_longitude
FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id
    AND p.primary_latitude IS NOT NULL AND p.primary_longitude IS NOT NULL
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id;

-- =============================================================================
SELECT DISTINCT o.id, pn.name, oe.email
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_sports os ON os.organization_id = o.id
JOIN sports s ON s.id = os.sport_id AND s.slug = 'jaakiekko'
JOIN organization_profile p ON p.organization_id = o.id
    AND p.primary_municipality_code = '837' AND p.has_email = 1
JOIN organization_emails oe ON oe.organization_id = o.id;
