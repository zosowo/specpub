"""
전자제품 스펙 카탈로그 — 2024~2025년 실제 출시 제품 기준.
specs 키는 functions.php specanalyzer_spec_schema() 와 일치.
"""

PRODUCTS = [

    # ══════════════════════════════════════════════════════════
    # 스마트폰
    # ══════════════════════════════════════════════════════════

    {"model":"Samsung Galaxy S25 Ultra","slug":"samsung-galaxy-s25-ultra","brand":"Samsung","category":"smartphone","release_year":"2025","specs":{"brand":"Samsung","chip":"Snapdragon 8 Elite","ram":"12","storage":"256 / 512 / 1024","display_size":"6.9","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"200","front_camera":"12","battery":"5000","charging":"45","weight":"218","price":"1890000","os":"Android 15 (One UI 7)"}},
    {"model":"Samsung Galaxy S25+","slug":"samsung-galaxy-s25-plus","brand":"Samsung","category":"smartphone","release_year":"2025","specs":{"brand":"Samsung","chip":"Snapdragon 8 Elite","ram":"12","storage":"256 / 512","display_size":"6.7","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"50","front_camera":"12","battery":"4900","charging":"45","weight":"190","price":"1380000","os":"Android 15 (One UI 7)"}},
    {"model":"Samsung Galaxy S25","slug":"samsung-galaxy-s25","brand":"Samsung","category":"smartphone","release_year":"2025","specs":{"brand":"Samsung","chip":"Snapdragon 8 Elite","ram":"12","storage":"128 / 256","display_size":"6.2","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"50","front_camera":"12","battery":"4000","charging":"25","weight":"162","price":"1155000","os":"Android 15 (One UI 7)"}},
    {"model":"Samsung Galaxy S25 Edge","slug":"samsung-galaxy-s25-edge","brand":"Samsung","category":"smartphone","release_year":"2025","specs":{"brand":"Samsung","chip":"Snapdragon 8 Elite","ram":"12","storage":"256","display_size":"6.7","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"200","front_camera":"12","battery":"3900","charging":"25","weight":"163","price":"1650000","os":"Android 15 (One UI 7)"}},
    {"model":"Samsung Galaxy Z Fold 6","slug":"samsung-galaxy-z-fold-6","brand":"Samsung","category":"smartphone","release_year":"2024","specs":{"brand":"Samsung","chip":"Snapdragon 8 Gen 3","ram":"12","storage":"256 / 512 / 1024","display_size":"7.6 (메인) / 6.3 (커버)","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"50","front_camera":"10","battery":"4400","charging":"25","weight":"239","price":"2198000","os":"Android 14 (One UI 6.1.1)"}},
    {"model":"Samsung Galaxy Z Flip 6","slug":"samsung-galaxy-z-flip-6","brand":"Samsung","category":"smartphone","release_year":"2024","specs":{"brand":"Samsung","chip":"Snapdragon 8 Gen 3","ram":"12","storage":"256 / 512","display_size":"6.7 (메인) / 3.4 (커버)","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"50","front_camera":"10","battery":"4000","charging":"25","weight":"187","price":"1398000","os":"Android 14 (One UI 6.1.1)"}},
    {"model":"Samsung Galaxy S24 Ultra","slug":"samsung-galaxy-s24-ultra","brand":"Samsung","category":"smartphone","release_year":"2024","specs":{"brand":"Samsung","chip":"Snapdragon 8 Gen 3","ram":"12","storage":"256 / 512 / 1024","display_size":"6.8","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","main_camera":"200","front_camera":"12","battery":"5000","charging":"45","weight":"232","price":"1799000","os":"Android 14 (One UI 6.1)"}},
    {"model":"Samsung Galaxy A55 5G","slug":"samsung-galaxy-a55","brand":"Samsung","category":"smartphone","release_year":"2024","specs":{"brand":"Samsung","chip":"Exynos 1480","ram":"8","storage":"128 / 256","display_size":"6.6","display_panel":"Super AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"32","battery":"5000","charging":"25","weight":"213","price":"569000","os":"Android 14 (One UI 6.1)"}},
    {"model":"Samsung Galaxy A35 5G","slug":"samsung-galaxy-a35","brand":"Samsung","category":"smartphone","release_year":"2024","specs":{"brand":"Samsung","chip":"Exynos 1380","ram":"6","storage":"128 / 256","display_size":"6.6","display_panel":"Super AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"13","battery":"5000","charging":"25","weight":"210","price":"449000","os":"Android 14 (One UI 6.1)"}},
    {"model":"Apple iPhone 16 Pro Max","slug":"apple-iphone-16-pro-max","brand":"Apple","category":"smartphone","release_year":"2024","specs":{"brand":"Apple","chip":"A18 Pro","ram":"8","storage":"256 / 512 / 1024","display_size":"6.9","display_panel":"Super Retina XDR OLED","refresh_rate":"120","main_camera":"48","front_camera":"12","battery":"4685","charging":"27","weight":"227","price":"1900000","os":"iOS 18"}},
    {"model":"Apple iPhone 16 Pro","slug":"apple-iphone-16-pro","brand":"Apple","category":"smartphone","release_year":"2024","specs":{"brand":"Apple","chip":"A18 Pro","ram":"8","storage":"128 / 256 / 512 / 1024","display_size":"6.3","display_panel":"Super Retina XDR OLED","refresh_rate":"120","main_camera":"48","front_camera":"12","battery":"3582","charging":"27","weight":"199","price":"1650000","os":"iOS 18"}},
    {"model":"Apple iPhone 16 Plus","slug":"apple-iphone-16-plus","brand":"Apple","category":"smartphone","release_year":"2024","specs":{"brand":"Apple","chip":"A18","ram":"8","storage":"128 / 256 / 512","display_size":"6.7","display_panel":"Super Retina XDR OLED","refresh_rate":"60","main_camera":"48","front_camera":"12","battery":"4674","charging":"25","weight":"203","price":"1450000","os":"iOS 18"}},
    {"model":"Apple iPhone 16","slug":"apple-iphone-16","brand":"Apple","category":"smartphone","release_year":"2024","specs":{"brand":"Apple","chip":"A18","ram":"8","storage":"128 / 256 / 512","display_size":"6.1","display_panel":"Super Retina XDR OLED","refresh_rate":"60","main_camera":"48","front_camera":"12","battery":"3561","charging":"25","weight":"170","price":"1250000","os":"iOS 18"}},
    {"model":"Google Pixel 9 Pro XL","slug":"google-pixel-9-pro-xl","brand":"Google","category":"smartphone","release_year":"2024","specs":{"brand":"Google","chip":"Google Tensor G4","ram":"16","storage":"128 / 256 / 512 / 1024","display_size":"6.8","display_panel":"LTPO OLED","refresh_rate":"120","main_camera":"50","front_camera":"10.5","battery":"5060","charging":"37","weight":"221","price":"1450000","os":"Android 14"}},
    {"model":"Google Pixel 9 Pro","slug":"google-pixel-9-pro","brand":"Google","category":"smartphone","release_year":"2024","specs":{"brand":"Google","chip":"Google Tensor G4","ram":"16","storage":"128 / 256 / 512 / 1024","display_size":"6.3","display_panel":"LTPO OLED","refresh_rate":"120","main_camera":"50","front_camera":"10.5","battery":"4700","charging":"37","weight":"199","price":"1300000","os":"Android 14"}},
    {"model":"Google Pixel 9","slug":"google-pixel-9","brand":"Google","category":"smartphone","release_year":"2024","specs":{"brand":"Google","chip":"Google Tensor G4","ram":"12","storage":"128 / 256","display_size":"6.3","display_panel":"OLED","refresh_rate":"120","main_camera":"50","front_camera":"10.5","battery":"4700","charging":"27","weight":"198","price":"999000","os":"Android 14"}},
    {"model":"Xiaomi 15 Ultra","slug":"xiaomi-15-ultra","brand":"Xiaomi","category":"smartphone","release_year":"2025","specs":{"brand":"Xiaomi","chip":"Snapdragon 8 Elite","ram":"16","storage":"512 / 1024","display_size":"6.73","display_panel":"LTPO AMOLED","refresh_rate":"120","main_camera":"200","front_camera":"32","battery":"5410","charging":"90","weight":"229","price":"1600000","os":"Android 15 (HyperOS 2)"}},
    {"model":"Xiaomi 15 Pro","slug":"xiaomi-15-pro","brand":"Xiaomi","category":"smartphone","release_year":"2025","specs":{"brand":"Xiaomi","chip":"Snapdragon 8 Elite","ram":"12","storage":"256 / 512","display_size":"6.73","display_panel":"LTPO AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"32","battery":"6100","charging":"90","weight":"213","price":"1200000","os":"Android 15 (HyperOS 2)"}},
    {"model":"Xiaomi 15","slug":"xiaomi-15","brand":"Xiaomi","category":"smartphone","release_year":"2025","specs":{"brand":"Xiaomi","chip":"Snapdragon 8 Elite","ram":"12","storage":"256 / 512","display_size":"6.36","display_panel":"OLED","refresh_rate":"120","main_camera":"50","front_camera":"32","battery":"5240","charging":"90","weight":"189","price":"950000","os":"Android 15 (HyperOS 2)"}},
    {"model":"OnePlus 13","slug":"oneplus-13","brand":"OnePlus","category":"smartphone","release_year":"2025","specs":{"brand":"OnePlus","chip":"Snapdragon 8 Elite","ram":"12","storage":"256 / 512","display_size":"6.82","display_panel":"LTPO AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"32","battery":"6000","charging":"100","weight":"210","price":"1100000","os":"Android 15 (OxygenOS 15)"}},
    {"model":"ASUS ROG Phone 9 Pro","slug":"asus-rog-phone-9-pro","brand":"ASUS","category":"smartphone","release_year":"2025","specs":{"brand":"ASUS","chip":"Snapdragon 8 Elite","ram":"16","storage":"512","display_size":"6.78","display_panel":"AMOLED","refresh_rate":"185","main_camera":"50","front_camera":"32","battery":"5800","charging":"65","weight":"227","price":"1500000","os":"Android 15 (ROG UI)"}},
    {"model":"Sony Xperia 1 VI","slug":"sony-xperia-1-vi","brand":"Sony","category":"smartphone","release_year":"2024","specs":{"brand":"Sony","chip":"Snapdragon 8 Gen 3","ram":"12","storage":"256 / 512","display_size":"6.5","display_panel":"4K OLED","refresh_rate":"120","main_camera":"48","front_camera":"12","battery":"5000","charging":"30","weight":"192","price":"1700000","os":"Android 14"}},
    {"model":"Motorola Edge 50 Ultra","slug":"motorola-edge-50-ultra","brand":"Motorola","category":"smartphone","release_year":"2024","specs":{"brand":"Motorola","chip":"Snapdragon 8s Gen 3","ram":"12","storage":"512","display_size":"6.7","display_panel":"pOLED","refresh_rate":"165","main_camera":"50","front_camera":"50","battery":"4500","charging":"125","weight":"197","price":"900000","os":"Android 14"}},
    {"model":"Nothing Phone (2a) Plus","slug":"nothing-phone-2a-plus","brand":"Nothing","category":"smartphone","release_year":"2024","specs":{"brand":"Nothing","chip":"MediaTek Dimensity 7350 Pro","ram":"12","storage":"256","display_size":"6.7","display_panel":"AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"32","battery":"5000","charging":"50","weight":"190","price":"499000","os":"Android 14 (Nothing OS 2.6)"}},
    {"model":"Realme GT 7 Pro","slug":"realme-gt-7-pro","brand":"Realme","category":"smartphone","release_year":"2024","specs":{"brand":"Realme","chip":"Snapdragon 8 Elite","ram":"12","storage":"256 / 512","display_size":"6.78","display_panel":"LTPO AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"16","battery":"6500","charging":"120","weight":"224","price":"850000","os":"Android 15 (realme UI 6)"}},
    {"model":"Vivo X200 Pro","slug":"vivo-x200-pro","brand":"Vivo","category":"smartphone","release_year":"2024","specs":{"brand":"Vivo","chip":"Dimensity 9400","ram":"16","storage":"256 / 512","display_size":"6.78","display_panel":"LTPO AMOLED","refresh_rate":"120","main_camera":"50","front_camera":"32","battery":"6000","charging":"90","weight":"229","price":"1200000","os":"Android 15 (OriginOS 5)"}},

    # ══════════════════════════════════════════════════════════
    # 노트북
    # ══════════════════════════════════════════════════════════

    {"model":"Apple MacBook Air M4 13인치","slug":"apple-macbook-air-m4-13","brand":"Apple","category":"laptop","release_year":"2025","specs":{"brand":"Apple","cpu":"Apple M4 (10코어)","gpu":"Apple M4 GPU (10코어)","ram":"16","storage":"256 / 512 / 1024","display_size":"13.6","display_resolution":"2560×1664","display_panel":"Liquid Retina IPS","battery":"52.6","weight":"1.24","os":"macOS Sequoia","price":"1690000"}},
    {"model":"Apple MacBook Air M4 15인치","slug":"apple-macbook-air-m4-15","brand":"Apple","category":"laptop","release_year":"2025","specs":{"brand":"Apple","cpu":"Apple M4 (10코어)","gpu":"Apple M4 GPU (10코어)","ram":"16","storage":"256 / 512 / 1024","display_size":"15.3","display_resolution":"2880×1864","display_panel":"Liquid Retina IPS","battery":"66.5","weight":"1.51","os":"macOS Sequoia","price":"2090000"}},
    {"model":"Apple MacBook Pro M4 14인치","slug":"apple-macbook-pro-m4-14","brand":"Apple","category":"laptop","release_year":"2024","specs":{"brand":"Apple","cpu":"Apple M4 (10코어)","gpu":"Apple M4 GPU (10코어)","ram":"16","storage":"512 / 1024","display_size":"14.2","display_resolution":"3024×1964","display_panel":"Liquid Retina XDR","battery":"72.0","weight":"1.55","os":"macOS Sequoia","price":"2290000"}},
    {"model":"Apple MacBook Pro M4 Pro 16인치","slug":"apple-macbook-pro-m4-pro-16","brand":"Apple","category":"laptop","release_year":"2024","specs":{"brand":"Apple","cpu":"Apple M4 Pro (14코어)","gpu":"Apple M4 Pro GPU (20코어)","ram":"24","storage":"512 / 1024","display_size":"16.2","display_resolution":"3456×2234","display_panel":"Liquid Retina XDR","battery":"100.0","weight":"2.14","os":"macOS Sequoia","price":"3990000"}},
    {"model":"Samsung Galaxy Book5 Pro 360","slug":"samsung-galaxy-book5-pro-360","brand":"Samsung","category":"laptop","release_year":"2025","specs":{"brand":"Samsung","cpu":"Intel Core Ultra 7 258V","gpu":"Intel Arc 140V","ram":"16","storage":"512 / 1024","display_size":"16","display_resolution":"2880×1800","display_panel":"Dynamic AMOLED 2X","battery":"76","weight":"1.75","os":"Windows 11 Home","price":"2490000"}},
    {"model":"Samsung Galaxy Book5 Pro","slug":"samsung-galaxy-book5-pro","brand":"Samsung","category":"laptop","release_year":"2025","specs":{"brand":"Samsung","cpu":"Intel Core Ultra 7 258V","gpu":"Intel Arc 140V","ram":"16","storage":"512 / 1024","display_size":"16","display_resolution":"2880×1800","display_panel":"AMOLED","battery":"76","weight":"1.56","os":"Windows 11 Home","price":"2290000"}},
    {"model":"LG gram 17 2025","slug":"lg-gram-17-2025","brand":"LG","category":"laptop","release_year":"2025","specs":{"brand":"LG","cpu":"Intel Core Ultra 7 258V","gpu":"Intel Arc 140V","ram":"32","storage":"1024","display_size":"17","display_resolution":"2560×1600","display_panel":"IPS","battery":"90","weight":"1.35","os":"Windows 11 Home","price":"2290000"}},
    {"model":"LG gram 16 2025","slug":"lg-gram-16-2025","brand":"LG","category":"laptop","release_year":"2025","specs":{"brand":"LG","cpu":"Intel Core Ultra 7 258V","gpu":"Intel Arc 140V","ram":"32","storage":"1024","display_size":"16","display_resolution":"2560×1600","display_panel":"IPS","battery":"80","weight":"1.19","os":"Windows 11 Home","price":"1990000"}},
    {"model":"ASUS Zenbook S 16","slug":"asus-zenbook-s16-2025","brand":"ASUS","category":"laptop","release_year":"2025","specs":{"brand":"ASUS","cpu":"AMD Ryzen AI 9 HX 370","gpu":"AMD Radeon 890M","ram":"32","storage":"1024","display_size":"16","display_resolution":"3200×2000","display_panel":"OLED","battery":"78","weight":"1.5","os":"Windows 11 Home","price":"1990000"}},
    {"model":"ASUS ROG Zephyrus G16 2025","slug":"asus-rog-zephyrus-g16-2025","brand":"ASUS","category":"laptop","release_year":"2025","specs":{"brand":"ASUS","cpu":"Intel Core Ultra 9 185H","gpu":"NVIDIA GeForce RTX 4090","ram":"32","storage":"1024","display_size":"16","display_resolution":"2560×1600","display_panel":"OLED","battery":"90","weight":"1.85","os":"Windows 11 Home","price":"4290000"}},
    {"model":"Dell XPS 15 2024","slug":"dell-xps-15-2024","brand":"Dell","category":"laptop","release_year":"2024","specs":{"brand":"Dell","cpu":"Intel Core Ultra 9 185H","gpu":"NVIDIA RTX 4060","ram":"32","storage":"1024","display_size":"15.6","display_resolution":"3456×2160","display_panel":"OLED","battery":"86","weight":"1.86","os":"Windows 11 Home","price":"2890000"}},
    {"model":"Lenovo ThinkPad X1 Carbon Gen 13","slug":"lenovo-thinkpad-x1-carbon-gen13","brand":"Lenovo","category":"laptop","release_year":"2025","specs":{"brand":"Lenovo","cpu":"Intel Core Ultra 7 258V","gpu":"Intel Arc 140V","ram":"32","storage":"512 / 1024","display_size":"14","display_resolution":"2560×1600","display_panel":"IPS","battery":"57","weight":"1.12","os":"Windows 11 Pro","price":"2500000"}},
    {"model":"Lenovo IdeaPad Slim 5x 14","slug":"lenovo-ideapad-slim-5x-14","brand":"Lenovo","category":"laptop","release_year":"2024","specs":{"brand":"Lenovo","cpu":"Snapdragon X Plus (X1P-64-100)","gpu":"Adreno X1","ram":"16","storage":"512","display_size":"14.5","display_resolution":"2944×1840","display_panel":"IPS","battery":"56","weight":"1.44","os":"Windows 11 Home","price":"1290000"}},
    {"model":"HP Spectre x360 14 2025","slug":"hp-spectre-x360-14-2025","brand":"HP","category":"laptop","release_year":"2025","specs":{"brand":"HP","cpu":"Intel Core Ultra 7 258V","gpu":"Intel Arc 140V","ram":"32","storage":"1024","display_size":"14","display_resolution":"2880×1920","display_panel":"OLED","battery":"72","weight":"1.36","os":"Windows 11 Home","price":"2300000"}},
    {"model":"Microsoft Surface Laptop 7 15인치","slug":"microsoft-surface-laptop-7-15","brand":"Microsoft","category":"laptop","release_year":"2024","specs":{"brand":"Microsoft","cpu":"Snapdragon X Elite X1E-80-100","gpu":"Adreno X1","ram":"16","storage":"512 / 1024","display_size":"15","display_resolution":"2496×1664","display_panel":"PixelSense IPS","battery":"54","weight":"1.66","os":"Windows 11 Home","price":"2299000"}},
    {"model":"Razer Blade 15 2024","slug":"razer-blade-15-2024","brand":"Razer","category":"laptop","release_year":"2024","specs":{"brand":"Razer","cpu":"Intel Core i9-14900HX","gpu":"NVIDIA RTX 4080","ram":"32","storage":"1024","display_size":"15.6","display_resolution":"2560×1440","display_panel":"QHD OLED","battery":"95.2","weight":"2.07","os":"Windows 11 Home","price":"4500000"}},

    # ══════════════════════════════════════════════════════════
    # 태블릿
    # ══════════════════════════════════════════════════════════

    {"model":"Apple iPad Pro M4 13인치","slug":"apple-ipad-pro-m4-13","brand":"Apple","category":"tablet","release_year":"2024","specs":{"brand":"Apple","chip":"Apple M4","ram":"16","storage":"256 / 512 / 1024 / 2048","display_size":"13","display_panel":"Ultra Retina XDR OLED","refresh_rate":"120","battery":"10290","weight":"579","os":"iPadOS 17","price":"1899000"}},
    {"model":"Apple iPad Pro M4 11인치","slug":"apple-ipad-pro-m4-11","brand":"Apple","category":"tablet","release_year":"2024","specs":{"brand":"Apple","chip":"Apple M4","ram":"8","storage":"256 / 512 / 1024 / 2048","display_size":"11","display_panel":"Ultra Retina XDR OLED","refresh_rate":"120","battery":"7606","weight":"444","os":"iPadOS 17","price":"1299000"}},
    {"model":"Apple iPad Air M3 13인치","slug":"apple-ipad-air-m3-13","brand":"Apple","category":"tablet","release_year":"2025","specs":{"brand":"Apple","chip":"Apple M3","ram":"8","storage":"128 / 256 / 512 / 1024","display_size":"13","display_panel":"Liquid Retina IPS","refresh_rate":"60","battery":"9720","weight":"617","os":"iPadOS 18","price":"1299000"}},
    {"model":"Apple iPad Air M3 11인치","slug":"apple-ipad-air-m3-11","brand":"Apple","category":"tablet","release_year":"2025","specs":{"brand":"Apple","chip":"Apple M3","ram":"8","storage":"128 / 256 / 512 / 1024","display_size":"11","display_panel":"Liquid Retina IPS","refresh_rate":"60","battery":"7606","weight":"462","os":"iPadOS 18","price":"999000"}},
    {"model":"Apple iPad mini 7","slug":"apple-ipad-mini-7","brand":"Apple","category":"tablet","release_year":"2024","specs":{"brand":"Apple","chip":"Apple A17 Pro","ram":"8","storage":"128 / 256 / 512","display_size":"8.3","display_panel":"Liquid Retina IPS","refresh_rate":"60","battery":"5078","weight":"293","os":"iPadOS 18","price":"799000"}},
    {"model":"Samsung Galaxy Tab S10 Ultra","slug":"samsung-galaxy-tab-s10-ultra","brand":"Samsung","category":"tablet","release_year":"2024","specs":{"brand":"Samsung","chip":"Snapdragon 8 Gen 3","ram":"12","storage":"256 / 512","display_size":"14.6","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","battery":"11200","weight":"718","os":"Android 14 (One UI 6.1)","price":"1699000"}},
    {"model":"Samsung Galaxy Tab S10+","slug":"samsung-galaxy-tab-s10-plus","brand":"Samsung","category":"tablet","release_year":"2024","specs":{"brand":"Samsung","chip":"Snapdragon 8 Gen 3","ram":"12","storage":"256 / 512","display_size":"12.4","display_panel":"Dynamic AMOLED 2X","refresh_rate":"120","battery":"10090","weight":"581","os":"Android 14 (One UI 6.1)","price":"1299000"}},
    {"model":"Samsung Galaxy Tab S10 FE","slug":"samsung-galaxy-tab-s10-fe","brand":"Samsung","category":"tablet","release_year":"2025","specs":{"brand":"Samsung","chip":"Exynos 1580","ram":"8","storage":"128 / 256","display_size":"10.9","display_panel":"TFT LCD","refresh_rate":"90","battery":"8000","weight":"523","os":"Android 15 (One UI 7)","price":"599000"}},
    {"model":"Lenovo Tab P12 Pro 2024","slug":"lenovo-tab-p12-pro-2024","brand":"Lenovo","category":"tablet","release_year":"2024","specs":{"brand":"Lenovo","chip":"MediaTek Dimensity 9000","ram":"12","storage":"256","display_size":"12.6","display_panel":"AMOLED","refresh_rate":"120","battery":"10200","weight":"565","os":"Android 13","price":"899000"}},
    {"model":"Microsoft Surface Pro 11","slug":"microsoft-surface-pro-11","brand":"Microsoft","category":"tablet","release_year":"2024","specs":{"brand":"Microsoft","chip":"Snapdragon X Elite","ram":"16","storage":"512 / 1024","display_size":"13","display_panel":"PixelSense IPS","refresh_rate":"120","battery":"53","weight":"895","os":"Windows 11 Home","price":"1799000"}},

    # ══════════════════════════════════════════════════════════
    # 이어폰 / 헤드폰
    # ══════════════════════════════════════════════════════════

    {"model":"Apple AirPods Pro 2","slug":"apple-airpods-pro-2","brand":"Apple","category":"earphone","release_year":"2024","specs":{"brand":"Apple","type":"커널형 인이어","driver":"11","anc":"지원 (H2 칩)","battery_bud":"6","battery_case":"30","codec":"AAC","weight_bud":"5.3","price":"359000"}},
    {"model":"Apple AirPods 4 ANC","slug":"apple-airpods-4-anc","brand":"Apple","category":"earphone","release_year":"2024","specs":{"brand":"Apple","type":"오픈핏 인이어","driver":"11","anc":"지원","battery_bud":"5","battery_case":"30","codec":"AAC","weight_bud":"4.3","price":"249000"}},
    {"model":"Apple AirPods 4","slug":"apple-airpods-4","brand":"Apple","category":"earphone","release_year":"2024","specs":{"brand":"Apple","type":"오픈핏 인이어","driver":"11","anc":"미지원","battery_bud":"5","battery_case":"30","codec":"AAC","weight_bud":"4.3","price":"189000"}},
    {"model":"Samsung Galaxy Buds 3 Pro","slug":"samsung-galaxy-buds-3-pro","brand":"Samsung","category":"earphone","release_year":"2024","specs":{"brand":"Samsung","type":"커널형 인이어","driver":"10.5","anc":"지원","battery_bud":"6","battery_case":"30","codec":"AAC, SBC, SSC HiFi","weight_bud":"5.5","price":"259000"}},
    {"model":"Samsung Galaxy Buds 3","slug":"samsung-galaxy-buds-3","brand":"Samsung","category":"earphone","release_year":"2024","specs":{"brand":"Samsung","type":"오픈핏 인이어","driver":"11","anc":"지원","battery_bud":"6","battery_case":"30","codec":"AAC, SBC, SSC HiFi","weight_bud":"4.9","price":"199000"}},
    {"model":"Sony WF-1000XM5","slug":"sony-wf-1000xm5","brand":"Sony","category":"earphone","release_year":"2023","specs":{"brand":"Sony","type":"커널형 인이어","driver":"8.4","anc":"지원 (QN2e 칩)","battery_bud":"8","battery_case":"24","codec":"AAC, SBC, LDAC","weight_bud":"5.9","price":"349000"}},
    {"model":"Sony WH-1000XM5","slug":"sony-wh-1000xm5","brand":"Sony","category":"earphone","release_year":"2022","specs":{"brand":"Sony","type":"오버이어 헤드폰","driver":"30","anc":"지원 (HD NC 프로세서 QN1)","battery_bud":"30","battery_case":"0","codec":"AAC, SBC, LDAC, aptX","weight_bud":"250","price":"379000"}},
    {"model":"Bose QuietComfort Ultra Earbuds","slug":"bose-quietcomfort-ultra-earbuds","brand":"Bose","category":"earphone","release_year":"2023","specs":{"brand":"Bose","type":"커널형 인이어","driver":"9.3","anc":"지원 (CustomTune)","battery_bud":"6","battery_case":"24","codec":"AAC, SBC","weight_bud":"6.2","price":"399000"}},
    {"model":"Bose QuietComfort Ultra Headphones","slug":"bose-quietcomfort-ultra-headphones","brand":"Bose","category":"earphone","release_year":"2023","specs":{"brand":"Bose","type":"오버이어 헤드폰","driver":"40","anc":"지원 (CustomTune)","battery_bud":"24","battery_case":"0","codec":"AAC, SBC","weight_bud":"250","price":"449000"}},
    {"model":"Sennheiser Momentum 4 Wireless","slug":"sennheiser-momentum-4-wireless","brand":"Sennheiser","category":"earphone","release_year":"2022","specs":{"brand":"Sennheiser","type":"오버이어 헤드폰","driver":"42","anc":"지원","battery_bud":"60","battery_case":"0","codec":"AAC, SBC, aptX, aptX Adaptive","weight_bud":"293","price":"399000"}},
    {"model":"Nothing Ear (2)","slug":"nothing-ear-2","brand":"Nothing","category":"earphone","release_year":"2023","specs":{"brand":"Nothing","type":"커널형 인이어","driver":"11.6","anc":"지원","battery_bud":"6.3","battery_case":"36","codec":"AAC, SBC, LHDC 5.0","weight_bud":"4.5","price":"169000"}},
    {"model":"Jabra Elite 10","slug":"jabra-elite-10","brand":"Jabra","category":"earphone","release_year":"2023","specs":{"brand":"Jabra","type":"커널형 인이어","driver":"10","anc":"지원 (Advanced ANC)","battery_bud":"6","battery_case":"27","codec":"AAC, SBC, LC3","weight_bud":"5.9","price":"279000"}},

    # ══════════════════════════════════════════════════════════
    # 스마트워치
    # ══════════════════════════════════════════════════════════

    {"model":"Apple Watch Series 10","slug":"apple-watch-series-10","brand":"Apple","category":"smartwatch","release_year":"2024","specs":{"brand":"Apple","chip":"S10","display_size":"42 / 46","display_panel":"LTPO OLED","battery":"308 / 316","battery_life":"18시간","health":"심전도, 혈중산소, 피부온도 측정","weight":"36.4 / 41.7","os":"watchOS 11","price":"599000"}},
    {"model":"Apple Watch Ultra 2","slug":"apple-watch-ultra-2","brand":"Apple","category":"smartwatch","release_year":"2024","specs":{"brand":"Apple","chip":"S9","display_size":"49","display_panel":"LTPO OLED","battery":"542","battery_life":"36시간 (저전력 60시간)","health":"심전도, 혈중산소, 수심, 온도 측정","weight":"61.4","os":"watchOS 11","price":"1249000"}},
    {"model":"Samsung Galaxy Watch 7","slug":"samsung-galaxy-watch-7","brand":"Samsung","category":"smartwatch","release_year":"2024","specs":{"brand":"Samsung","chip":"Exynos W1000","display_size":"40 / 44","display_panel":"Super AMOLED","battery":"300 / 425","battery_life":"40시간","health":"심전도, 혈압, 혈중산소, 체성분 측정","weight":"28.9 / 33.8","os":"Wear OS 5 (One UI Watch 6)","price":"379000"}},
    {"model":"Samsung Galaxy Watch Ultra","slug":"samsung-galaxy-watch-ultra","brand":"Samsung","category":"smartwatch","release_year":"2024","specs":{"brand":"Samsung","chip":"Exynos W1000","display_size":"47","display_panel":"Super AMOLED","battery":"590","battery_life":"60시간","health":"심전도, 혈압, 혈중산소, 체성분, 피부온도 측정","weight":"60.5","os":"Wear OS 5 (One UI Watch 6)","price":"799000"}},
    {"model":"Google Pixel Watch 3 45mm","slug":"google-pixel-watch-3-45","brand":"Google","category":"smartwatch","release_year":"2024","specs":{"brand":"Google","chip":"Google Tensor G3","display_size":"45","display_panel":"AMOLED","battery":"420","battery_life":"24시간","health":"심전도, 혈중산소, 피부전도 측정","weight":"37","os":"Wear OS 4","price":"499000"}},
    {"model":"Garmin Fenix 8 Solar","slug":"garmin-fenix-8-solar","brand":"Garmin","category":"smartwatch","release_year":"2024","specs":{"brand":"Garmin","chip":"Garmin 5x Plus","display_size":"51","display_panel":"MIP (Solar)","battery":"1050","battery_life":"29일 (스마트워치) / 태양광 무제한","health":"심박수, 혈중산소, 스트레스, 수면 분석","weight":"89","os":"Garmin OS","price":"1199000"}},
    {"model":"Garmin Forerunner 965","slug":"garmin-forerunner-965","brand":"Garmin","category":"smartwatch","release_year":"2023","specs":{"brand":"Garmin","chip":"Garmin 5x Plus","display_size":"47","display_panel":"AMOLED","battery":"570","battery_life":"23일","health":"심박수, VO2 Max, HRV, 혈중산소 측정","weight":"53","os":"Garmin OS","price":"729000"}},
    {"model":"Amazfit Balance 2","slug":"amazfit-balance-2","brand":"Amazfit","category":"smartwatch","release_year":"2025","specs":{"brand":"Amazfit","chip":"Zepp OS","display_size":"46","display_panel":"AMOLED","battery":"465","battery_life":"16일","health":"심박수, 혈중산소, 스트레스, 수면 분석","weight":"31","os":"Zepp OS 4","price":"329000"}},

    # ══════════════════════════════════════════════════════════
    # TV
    # ══════════════════════════════════════════════════════════

    {"model":"Samsung Neo QLED 8K QN900D 85인치","slug":"samsung-neo-qled-8k-qn900d-85","brand":"Samsung","category":"tv","release_year":"2024","specs":{"brand":"Samsung","screen_size":"85","panel":"Neo QLED (Mini LED)","resolution":"8K (7680×4320)","refresh_rate":"120","hdr":"HDR10+, HLG","smart_os":"Tizen OS 8","sound_output":"100","price":"18000000"}},
    {"model":"Samsung Neo QLED 4K QN85D 65인치","slug":"samsung-neo-qled-4k-qn85d-65","brand":"Samsung","category":"tv","release_year":"2024","specs":{"brand":"Samsung","screen_size":"65","panel":"Neo QLED (Mini LED)","resolution":"4K (3840×2160)","refresh_rate":"144","hdr":"HDR10+, HLG","smart_os":"Tizen OS 8","sound_output":"60","price":"3500000"}},
    {"model":"Samsung OLED S90D 65인치","slug":"samsung-oled-s90d-65","brand":"Samsung","category":"tv","release_year":"2024","specs":{"brand":"Samsung","screen_size":"65","panel":"OLED","resolution":"4K (3840×2160)","refresh_rate":"144","hdr":"HDR10+, Dolby Vision","smart_os":"Tizen OS 8","sound_output":"60","price":"4200000"}},
    {"model":"Samsung The Frame 2025 65인치","slug":"samsung-the-frame-2025-65","brand":"Samsung","category":"tv","release_year":"2025","specs":{"brand":"Samsung","screen_size":"65","panel":"QLED","resolution":"4K (3840×2160)","refresh_rate":"120","hdr":"HDR10+","smart_os":"Tizen OS 8","sound_output":"40","price":"2800000"}},
    {"model":"LG OLED G5 77인치","slug":"lg-oled-g5-77","brand":"LG","category":"tv","release_year":"2025","specs":{"brand":"LG","screen_size":"77","panel":"OLED evo (MLA)","resolution":"4K (3840×2160)","refresh_rate":"144","hdr":"Dolby Vision IQ, HDR10, HLG","smart_os":"webOS 25","sound_output":"60","price":"6900000"}},
    {"model":"LG OLED C5 65인치","slug":"lg-oled-c5-65","brand":"LG","category":"tv","release_year":"2025","specs":{"brand":"LG","screen_size":"65","panel":"OLED evo","resolution":"4K (3840×2160)","refresh_rate":"144","hdr":"Dolby Vision IQ, HDR10, HLG","smart_os":"webOS 25","sound_output":"60","price":"3900000"}},
    {"model":"LG OLED C5 55인치","slug":"lg-oled-c5-55","brand":"LG","category":"tv","release_year":"2025","specs":{"brand":"LG","screen_size":"55","panel":"OLED evo","resolution":"4K (3840×2160)","refresh_rate":"120","hdr":"Dolby Vision IQ, HDR10, HLG","smart_os":"webOS 25","sound_output":"40","price":"2500000"}},
    {"model":"Sony BRAVIA 9 85인치","slug":"sony-bravia-9-85","brand":"Sony","category":"tv","release_year":"2024","specs":{"brand":"Sony","screen_size":"85","panel":"Mini LED LCD","resolution":"4K (3840×2160)","refresh_rate":"144","hdr":"Dolby Vision, HDR10, HLG","smart_os":"Google TV","sound_output":"90","price":"8000000"}},
    {"model":"Sony BRAVIA 8 77인치","slug":"sony-bravia-8-77","brand":"Sony","category":"tv","release_year":"2024","specs":{"brand":"Sony","screen_size":"77","panel":"OLED","resolution":"4K (3840×2160)","refresh_rate":"120","hdr":"Dolby Vision, HDR10, HLG","smart_os":"Google TV","sound_output":"60","price":"5500000"}},
    {"model":"Philips OLED+959 65인치","slug":"philips-oled-959-65","brand":"Philips","category":"tv","release_year":"2024","specs":{"brand":"Philips","screen_size":"65","panel":"OLED","resolution":"4K (3840×2160)","refresh_rate":"144","hdr":"Dolby Vision, HDR10+","smart_os":"Google TV (Ambilight 4-sided)","sound_output":"90","price":"4500000"}},

    # ══════════════════════════════════════════════════════════
    # 모니터
    # ══════════════════════════════════════════════════════════

    {"model":"LG UltraGear OLED 27GS95QE","slug":"lg-ultragear-oled-27gs95qe","brand":"LG","category":"monitor","release_year":"2024","specs":{"brand":"LG","screen_size":"27","panel":"OLED","resolution":"2560×1440 (QHD)","refresh_rate":"240","response_time":"0.03","hdr":"HDR400 True Black","ports":"HDMI 2.1, DP 1.4, USB-C","price":"1099000"}},
    {"model":"Samsung Odyssey OLED G8 34인치","slug":"samsung-odyssey-oled-g8-34","brand":"Samsung","category":"monitor","release_year":"2024","specs":{"brand":"Samsung","screen_size":"34","panel":"OLED (곡면)","resolution":"3440×1440 (UWQHD)","refresh_rate":"175","response_time":"0.1","hdr":"DisplayHDR True Black 400","ports":"HDMI 2.1×2, DP 1.4, USB-C 90W","price":"1299000"}},
    {"model":"ASUS ROG Swift PG27AQDP","slug":"asus-rog-swift-pg27aqdp","brand":"ASUS","category":"monitor","release_year":"2024","specs":{"brand":"ASUS","screen_size":"27","panel":"OLED","resolution":"2560×1440 (QHD)","refresh_rate":"240","response_time":"0.03","hdr":"HDR True Black 400","ports":"HDMI 2.1, DP 1.4, USB-C","price":"999000"}},
    {"model":"Dell UltraSharp U3224KB","slug":"dell-ultrasharp-u3224kb","brand":"Dell","category":"monitor","release_year":"2024","specs":{"brand":"Dell","screen_size":"32","panel":"IPS Black","resolution":"6144×3456 (6K)","refresh_rate":"60","response_time":"5","hdr":"DisplayHDR 600","ports":"Thunderbolt 4, HDMI 2.1, DP 1.4","price":"2500000"}},
    {"model":"LG UltraWide 34WP85C-B","slug":"lg-ultrawide-34wp85c","brand":"LG","category":"monitor","release_year":"2023","specs":{"brand":"LG","screen_size":"34","panel":"Nano IPS (곡면)","resolution":"3440×1440 (UWQHD)","refresh_rate":"160","response_time":"1","hdr":"HDR10","ports":"HDMI 2.0×2, DP 1.0, USB-C 96W","price":"699000"}},

    # ══════════════════════════════════════════════════════════
    # 냉장고
    # ══════════════════════════════════════════════════════════

    {"model":"삼성 비스포크 냉장고 4도어 RF85DB99B5W 868L","slug":"samsung-bespoke-4door-rf85db99b5w","brand":"Samsung","category":"refrigerator","release_year":"2024","specs":{"brand":"Samsung","type":"4도어 (프렌치도어)","capacity":"868","fridge_vol":"603","freezer_vol":"265","energy_grade":"1","compressor":"디지털 인버터 (5스타 등급)","smart":"SmartThings 연동, AI 에너지 절약","noise":"43","color":"화이트 글라스","price":"4290000"}},
    {"model":"삼성 비스포크 냉장고 2도어 RL38CB662B 387L","slug":"samsung-bespoke-2door-387l","brand":"Samsung","category":"refrigerator","release_year":"2024","specs":{"brand":"Samsung","type":"상냉장 하냉동 (콤비)","capacity":"387","fridge_vol":"269","freezer_vol":"118","energy_grade":"1","compressor":"디지털 인버터","smart":"SmartThings 연동","noise":"40","color":"새틴 베이지","price":"1590000"}},
    {"model":"LG 디오스 오브제컬렉션 냉장고 T873ME111 873L","slug":"lg-dios-objet-t873me111","brand":"LG","category":"refrigerator","release_year":"2024","specs":{"brand":"LG","type":"4도어 (노크온)","capacity":"873","fridge_vol":"613","freezer_vol":"260","energy_grade":"1","compressor":"리니어 인버터","smart":"ThinQ 연동, 내부 카메라","noise":"43","color":"오브제 무광 베이지","price":"5190000"}},
    {"model":"LG 디오스 냉장고 3도어 K835AAF 835L","slug":"lg-dios-3door-835l","brand":"LG","category":"refrigerator","release_year":"2024","specs":{"brand":"LG","type":"3도어 (상냉장 하냉동)","capacity":"835","fridge_vol":"594","freezer_vol":"241","energy_grade":"1","compressor":"리니어 인버터","smart":"ThinQ 연동","noise":"43","color":"화이트","price":"2990000"}},
    {"model":"위니아 딤채 김치냉장고 스탠드 WDT42HRWAS 424L","slug":"winia-dimchae-stand-424l","brand":"위니아","category":"refrigerator","release_year":"2024","specs":{"brand":"위니아","type":"스탠드 김치냉장고","capacity":"424","fridge_vol":"424","freezer_vol":"0","energy_grade":"1","compressor":"인버터","smart":"Wi-Fi 연동","noise":"38","color":"화이트","price":"1590000"}},
    {"model":"LG 디오스 김치톡톡 K328MHB72 327L","slug":"lg-dios-kimchi-k328","brand":"LG","category":"refrigerator","release_year":"2024","specs":{"brand":"LG","type":"상단 서랍형 김치냉장고","capacity":"327","fridge_vol":"327","freezer_vol":"0","energy_grade":"1","compressor":"리니어 인버터","smart":"ThinQ 연동","noise":"38","color":"무광 그레이","price":"1490000"}},
    {"model":"Bosch 냉장고 KGN56AIE0N 505L","slug":"bosch-refrigerator-kgn56","brand":"Bosch","category":"refrigerator","release_year":"2024","specs":{"brand":"Bosch","type":"상냉장 하냉동 (콤비)","capacity":"505","fridge_vol":"348","freezer_vol":"157","energy_grade":"1","compressor":"인버터","smart":"Home Connect 연동","noise":"38","color":"스테인리스","price":"2190000"}},

    # ══════════════════════════════════════════════════════════
    # 세탁기
    # ══════════════════════════════════════════════════════════

    {"model":"삼성 그랑데 AI 세탁기 WF25BB6900 25kg","slug":"samsung-grande-ai-wf25bb6900","brand":"Samsung","category":"washing_machine","release_year":"2024","specs":{"brand":"Samsung","type":"드럼 세탁기","capacity":"25","dry_capacity":"0","rpm":"1400","energy_grade":"1","noise_wash":"52","smart":"SmartThings, AI 세제 자동투입","price":"1990000"}},
    {"model":"삼성 그랑데 AI 건조겸용 WD17BB6400 17kg+10kg","slug":"samsung-grande-wd17bb6400","brand":"Samsung","category":"washing_machine","release_year":"2024","specs":{"brand":"Samsung","type":"드럼 세탁건조기","capacity":"17","dry_capacity":"10","rpm":"1400","energy_grade":"1","noise_wash":"52","smart":"SmartThings, AI 세제 자동투입","price":"2490000"}},
    {"model":"LG 트롬 오브제컬렉션 F25VQSK 25kg","slug":"lg-trom-objet-f25vqsk","brand":"LG","category":"washing_machine","release_year":"2024","specs":{"brand":"LG","type":"드럼 세탁기","capacity":"25","dry_capacity":"0","rpm":"1200","energy_grade":"1","noise_wash":"50","smart":"ThinQ, AI DD 모터","price":"2090000"}},
    {"model":"LG 트롬 세탁건조기 워시콤보 FX25VSK 25kg+15kg","slug":"lg-trom-washcombo-fx25vsk","brand":"LG","category":"washing_machine","release_year":"2024","specs":{"brand":"LG","type":"일체형 세탁건조기","capacity":"25","dry_capacity":"15","rpm":"1200","energy_grade":"1","noise_wash":"50","smart":"ThinQ, AI DD 모터","price":"3490000"}},
    {"model":"Bosch 세탁기 WAX32M40KR 10kg","slug":"bosch-washing-machine-wax32m40","brand":"Bosch","category":"washing_machine","release_year":"2024","specs":{"brand":"Bosch","type":"드럼 세탁기","capacity":"10","dry_capacity":"0","rpm":"1600","energy_grade":"1","noise_wash":"47","smart":"Home Connect 연동","price":"1590000"}},
    {"model":"Electrolux 세탁건조기 EW9W161B 16kg+10kg","slug":"electrolux-ew9w161b","brand":"Electrolux","category":"washing_machine","release_year":"2024","specs":{"brand":"Electrolux","type":"드럼 세탁건조기","capacity":"16","dry_capacity":"10","rpm":"1400","energy_grade":"1","noise_wash":"53","smart":"Wi-Fi 연동","price":"2190000"}},

    # ══════════════════════════════════════════════════════════
    # 에어컨
    # ══════════════════════════════════════════════════════════

    {"model":"삼성 비스포크 무풍에어컨 갤러리 AF17B6174AB 16평형","slug":"samsung-bespoke-mufung-gallery-16py","brand":"Samsung","category":"air_conditioner","release_year":"2024","specs":{"brand":"Samsung","type":"스탠드형","cooling_area":"16","cooling_power":"5.6","energy_grade":"1","inverter":"디지털 인버터 부스터","noise_in":"21","smart":"SmartThings 연동, AI 자동제어","price":"2490000"}},
    {"model":"삼성 비스포크 무풍에어컨 스탠드 25평형","slug":"samsung-bespoke-mufung-stand-25py","brand":"Samsung","category":"air_conditioner","release_year":"2024","specs":{"brand":"Samsung","type":"스탠드형","cooling_area":"25","cooling_power":"8.5","energy_grade":"1","inverter":"디지털 인버터 부스터","noise_in":"27","smart":"SmartThings 연동","price":"1990000"}},
    {"model":"삼성 비스포크 무풍에어컨 벽걸이 16평형","slug":"samsung-bespoke-mufung-wall-16py","brand":"Samsung","category":"air_conditioner","release_year":"2024","specs":{"brand":"Samsung","type":"벽걸이형","cooling_area":"16","cooling_power":"5.6","energy_grade":"1","inverter":"디지털 인버터","noise_in":"19","smart":"SmartThings 연동","price":"990000"}},
    {"model":"LG 휘센 타워 에어컨 FQ17HDPAB 17평형","slug":"lg-whisen-tower-fq17hdpab","brand":"LG","category":"air_conditioner","release_year":"2024","specs":{"brand":"LG","type":"스탠드형 (타워)","cooling_area":"17","cooling_power":"5.9","energy_grade":"1","inverter":"듀얼 인버터","noise_in":"23","smart":"ThinQ 연동, AI 스마트제어","price":"1790000"}},
    {"model":"LG 휘센 벽걸이 에어컨 SQ18BDAWAS 18평형","slug":"lg-whisen-wall-sq18bdawas","brand":"LG","category":"air_conditioner","release_year":"2024","specs":{"brand":"LG","type":"벽걸이형","cooling_area":"18","cooling_power":"6.3","energy_grade":"1","inverter":"듀얼 인버터","noise_in":"19","smart":"ThinQ 연동","price":"890000"}},
    {"model":"Daikin 에어컨 SXS71KV2 20평형","slug":"daikin-aircon-sxs71kv2","brand":"Daikin","category":"air_conditioner","release_year":"2024","specs":{"brand":"Daikin","type":"스탠드형","cooling_area":"20","cooling_power":"7.1","energy_grade":"1","inverter":"인버터","noise_in":"44","smart":"Wi-Fi 연동","price":"2490000"}},

    # ══════════════════════════════════════════════════════════
    # 공기청정기
    # ══════════════════════════════════════════════════════════

    {"model":"삼성 비스포크 큐브 공기청정기 AX90T9080WSD","slug":"samsung-bespoke-cube-ax90t9080","brand":"Samsung","category":"air_purifier","release_year":"2024","specs":{"brand":"Samsung","coverage":"90","cadr":"1080","filter":"HEPA H13 + 활성탄 복합","noise":"22","smart":"SmartThings 연동, AI 자동제어","price":"699000"}},
    {"model":"LG 퓨리케어 360° AS204NDFA","slug":"lg-puricare-360-as204ndfa","brand":"LG","category":"air_purifier","release_year":"2024","specs":{"brand":"LG","coverage":"87","cadr":"1020","filter":"HEPA H13 + 탈취 복합","noise":"22","smart":"ThinQ 연동, PM1.0 센서","price":"649000"}},
    {"model":"Coway 아이콘 AP-1512HH","slug":"coway-icon-ap-1512hh","brand":"Coway","category":"air_purifier","release_year":"2024","specs":{"brand":"Coway","coverage":"49","cadr":"360","filter":"프리 + HEPA + 활성탄","noise":"22","smart":"오염도 표시","price":"349000"}},
    {"model":"Coway 아이콘2 AP-2021FH","slug":"coway-icon2-ap-2021fh","brand":"Coway","category":"air_purifier","release_year":"2024","specs":{"brand":"Coway","coverage":"68","cadr":"560","filter":"프리 + HEPA + 활성탄","noise":"22","smart":"Wi-Fi 연동","price":"499000"}},
    {"model":"Dyson Purifier Hot+Cool HP09","slug":"dyson-purifier-hot-cool-hp09","brand":"Dyson","category":"air_purifier","release_year":"2023","specs":{"brand":"Dyson","coverage":"81","cadr":"290","filter":"HEPA H13 + 활성탄","noise":"23","smart":"MyDyson 앱 연동, 난방/냉방 겸용","price":"899000"}},
    {"model":"Blueair Blue Pure 311i Max","slug":"blueair-blue-pure-311i-max","brand":"Blueair","category":"air_purifier","release_year":"2023","specs":{"brand":"Blueair","coverage":"48","cadr":"340","filter":"HEPASilent Ultra","noise":"24","smart":"Blueair 앱 연동","price":"399000"}},

    # ══════════════════════════════════════════════════════════
    # 로봇청소기
    # ══════════════════════════════════════════════════════════

    {"model":"Roborock S8 MaxV Ultra","slug":"roborock-s8-maxv-ultra","brand":"Roborock","category":"robot_vacuum","release_year":"2024","specs":{"brand":"Roborock","suction":"10000","battery_life":"180","mapping":"LiDAR + 카메라 AI 장애물 인식","mop":"VibraRise 3.0 (자동 들어올림)","dustbin":"0.35","noise":"67","smart":"App 연동, 자동 세척·건조·비움","price":"1799000"}},
    {"model":"Ecovacs Deebot X5 Pro Omni","slug":"ecovacs-deebot-x5-pro-omni","brand":"Ecovacs","category":"robot_vacuum","release_year":"2024","specs":{"brand":"Ecovacs","suction":"8700","battery_life":"200","mapping":"LiDAR + TrueDetect 3D","mop":"OZMO Turbo 3.0 (자동 들어올림)","dustbin":"0.42","noise":"66","smart":"App 연동, 자동 세척·건조·비움","price":"1499000"}},
    {"model":"삼성 비스포크 제트봇 AI+ VR50T95735W","slug":"samsung-bespoke-jetbot-ai-vr50t95735w","brand":"Samsung","category":"robot_vacuum","release_year":"2024","specs":{"brand":"Samsung","suction":"5300","battery_life":"120","mapping":"LiDAR + AI 카메라","mop":"기본 물걸레","dustbin":"0.3","noise":"70","smart":"SmartThings 연동","price":"1590000"}},
    {"model":"LG 코드제로 로봇청소기 R5 ThinQ","slug":"lg-cordzero-robot-r5","brand":"LG","category":"robot_vacuum","release_year":"2024","specs":{"brand":"LG","suction":"2700","battery_life":"120","mapping":"LiDAR","mop":"진동 물걸레","dustbin":"0.44","noise":"67","smart":"ThinQ 연동","price":"1190000"}},
    {"model":"Roborock Q7 Max+","slug":"roborock-q7-max-plus","brand":"Roborock","category":"robot_vacuum","release_year":"2023","specs":{"brand":"Roborock","suction":"4200","battery_life":"180","mapping":"LiDAR PreciSense","mop":"VibraRise (자동 들어올림)","dustbin":"0.47","noise":"65","smart":"App 연동, 자동 비움","price":"749000"}},

    # ══════════════════════════════════════════════════════════
    # 무선청소기
    # ══════════════════════════════════════════════════════════

    {"model":"Dyson V15 Detect Absolute","slug":"dyson-v15-detect-absolute","brand":"Dyson","category":"vacuum","release_year":"2023","specs":{"brand":"Dyson","suction":"240","battery_life":"60","filtration":"HEPA 5단계 (완전 밀봉)","dust_cap":"0.77","weight":"3.1","noise":"70","price":"1199000"}},
    {"model":"Dyson V12 Detect Slim","slug":"dyson-v12-detect-slim","brand":"Dyson","category":"vacuum","release_year":"2024","specs":{"brand":"Dyson","suction":"150","battery_life":"60","filtration":"HEPA 5단계 (완전 밀봉)","dust_cap":"0.35","weight":"2.2","noise":"69","price":"899000"}},
    {"model":"삼성 제트 청소기 VS20R9049TH","slug":"samsung-jet-vs20r9049th","brand":"Samsung","category":"vacuum","release_year":"2024","specs":{"brand":"Samsung","suction":"200","battery_life":"60","filtration":"5중 HEPA 필터","dust_cap":"0.8","weight":"2.7","noise":"73","price":"699000"}},
    {"model":"LG 코드제로 A9K AS9KHLAC","slug":"lg-cordzero-a9k-as9khlac","brand":"LG","category":"vacuum","release_year":"2024","specs":{"brand":"LG","suction":"200","battery_life":"120","filtration":"HEPA 13 등급","dust_cap":"1.0","weight":"3.1","noise":"71","price":"799000"}},
    {"model":"Dyson Airwrap Multi-Styler Complete","slug":"dyson-airwrap-complete","brand":"Dyson","category":"vacuum","release_year":"2024","specs":{"brand":"Dyson","suction":"0","battery_life":"0","filtration":"헤어 스타일러 (청소기 아님)","dust_cap":"0","weight":"0.69","noise":"0","price":"699000"}},

    # ══════════════════════════════════════════════════════════
    # 전자레인지
    # ══════════════════════════════════════════════════════════

    {"model":"삼성 비스포크 전자레인지 MS23DB5700","slug":"samsung-bespoke-ms23db5700","brand":"Samsung","category":"microwave","release_year":"2024","specs":{"brand":"Samsung","type":"단독 전자레인지","capacity":"23","power":"800","inverter":"미지원","smart":"미지원","price":"189000"}},
    {"model":"LG NeoChef 전자레인지 MS2336GIS 23L","slug":"lg-neochef-ms2336gis","brand":"LG","category":"microwave","release_year":"2024","specs":{"brand":"LG","type":"단독 전자레인지","capacity":"23","power":"1200","inverter":"스마트 인버터","smart":"미지원","price":"209000"}},
    {"model":"LG NeoChef 광파오븐 MJ3965BDS 39L","slug":"lg-neochef-mj3965bds","brand":"LG","category":"microwave","release_year":"2024","specs":{"brand":"LG","type":"광파오븐 (전자레인지+그릴+컨벡션)","capacity":"39","power":"1200","inverter":"스마트 인버터","smart":"미지원","price":"499000"}},
    {"model":"Panasonic 전자레인지 NN-ST765 32L","slug":"panasonic-nn-st765","brand":"Panasonic","category":"microwave","release_year":"2023","specs":{"brand":"Panasonic","type":"단독 전자레인지","capacity":"32","power":"1000","inverter":"인버터","smart":"미지원","price":"299000"}},
    {"model":"삼성 비스포크 오븐 NQ50DB3500B 50L","slug":"samsung-bespoke-oven-nq50db3500b","brand":"Samsung","category":"microwave","release_year":"2024","specs":{"brand":"Samsung","type":"전자레인지+컨벡션 오븐","capacity":"50","power":"1850","inverter":"미지원","smart":"Wi-Fi 연동","price":"699000"}},

    # ══════════════════════════════════════════════════════════
    # 헤어드라이어
    # ══════════════════════════════════════════════════════════

    {"model":"Dyson Supersonic HD15","slug":"dyson-supersonic-hd15","brand":"Dyson","category":"hair_dryer","release_year":"2024","specs":{"brand":"Dyson","power":"1600","motor":"Dyson V9 디지털 모터 (110,000rpm)","speeds":"3","heat":"4 (Cold Shot 포함)","feature":"이온 제어, 자기 연결 부착물","weight":"641","price":"699000"}},
    {"model":"Panasonic 나노케어 헤어드라이어 EH-NA98","slug":"panasonic-nanoe-eh-na98","brand":"Panasonic","category":"hair_dryer","release_year":"2024","specs":{"brand":"Panasonic","power":"1800","motor":"AC 모터","speeds":"2","heat":"4","feature":"나노이 미네랄 기술, 스칼프 모드","weight":"620","price":"299000"}},
    {"model":"Remington D6094B Proluxe 2200W","slug":"remington-d6094b-proluxe","brand":"Remington","category":"hair_dryer","release_year":"2023","specs":{"brand":"Remington","power":"2200","motor":"DC 모터","speeds":"3","heat":"3","feature":"이온 발생, 세라믹 코팅","weight":"570","price":"119000"}},
    {"model":"GHD Helios 헤어드라이어","slug":"ghd-helios","brand":"GHD","category":"hair_dryer","release_year":"2023","specs":{"brand":"GHD","power":"2100","motor":"AC 모터","speeds":"2","heat":"3","feature":"이온 기술, 1900W 집중 건조","weight":"550","price":"269000"}},
    {"model":"Philips ThermoProtect BHD358 2300W","slug":"philips-thermoprotect-bhd358","brand":"Philips","category":"hair_dryer","release_year":"2024","specs":{"brand":"Philips","power":"2300","motor":"DC 모터","speeds":"2","heat":"3","feature":"ThermoProtect 기술, 이온 케어","weight":"590","price":"89000"}},

    # ══════════════════════════════════════════════════════════
    # 전기면도기
    # ══════════════════════════════════════════════════════════

    {"model":"Braun Series 9 Pro+ 9590cc","slug":"braun-series-9-pro-9590cc","brand":"Braun","category":"electric_shaver","release_year":"2024","specs":{"brand":"Braun","type":"왕복식","blades":"5중 (ProTex Flex)","battery_life":"60","charge_time":"1","waterproof":"IPX7","wet_dry":"물면도·건식 모두 사용","price":"599000"}},
    {"model":"Braun Series 7 7071cc","slug":"braun-series-7-7071cc","brand":"Braun","category":"electric_shaver","release_year":"2024","specs":{"brand":"Braun","type":"왕복식","blades":"4중","battery_life":"50","charge_time":"1","waterproof":"IPX7","wet_dry":"물면도·건식 모두 사용","price":"399000"}},
    {"model":"Philips 9000 Prestige SP9883","slug":"philips-9000-prestige-sp9883","brand":"Philips","category":"electric_shaver","release_year":"2024","specs":{"brand":"Philips","type":"회전식","blades":"3헤드 (SkinIQ)","battery_life":"60","charge_time":"1","waterproof":"IPX7","wet_dry":"물면도·건식 모두 사용","price":"499000"}},
    {"model":"Philips Series 7000 S7783","slug":"philips-series-7000-s7783","brand":"Philips","category":"electric_shaver","release_year":"2023","specs":{"brand":"Philips","type":"회전식","blades":"3헤드 (V-Track)","battery_life":"60","charge_time":"1","waterproof":"IPX7","wet_dry":"물면도·건식 모두 사용","price":"299000"}},
    {"model":"Panasonic ES-LS9AX Arc6","slug":"panasonic-arc6-es-ls9ax","brand":"Panasonic","category":"electric_shaver","release_year":"2024","specs":{"brand":"Panasonic","type":"왕복식","blades":"6중 (Arc6)","battery_life":"50","charge_time":"1","waterproof":"IPX7","wet_dry":"물면도·건식 모두 사용","price":"699000"}},
    {"model":"Panasonic ES-LV67 Arc5","slug":"panasonic-arc5-es-lv67","brand":"Panasonic","category":"electric_shaver","release_year":"2023","specs":{"brand":"Panasonic","type":"왕복식","blades":"5중 (Arc5)","battery_life":"45","charge_time":"1","waterproof":"IPX7","wet_dry":"물면도·건식 모두 사용","price":"399000"}},

    # ══════════════════════════════════════════════════════════
    # 음식물처리기
    # ══════════════════════════════════════════════════════════

    {"model":"SK매직 음식물처리기 EFD-C01WS","slug":"sk-magic-food-processor-efd-c01ws","brand":"SK매직","category":"food_processor","release_year":"2024","specs":{"brand":"SK매직","method":"건조분쇄","capacity":"1.5","daily":"0.8","noise":"45","smart":"미지원","price":"590000"}},
    {"model":"LG 음식물처리기 WF-G2WT","slug":"lg-food-processor-wf-g2wt","brand":"LG","category":"food_processor","release_year":"2024","specs":{"brand":"LG","method":"건조분쇄","capacity":"1.0","daily":"0.5","noise":"42","smart":"ThinQ 연동","price":"690000"}},
    {"model":"한일 음식물처리기 HFD-B01","slug":"hanil-food-processor-hfd-b01","brand":"한일","category":"food_processor","release_year":"2024","specs":{"brand":"한일","method":"건조분쇄","capacity":"1.0","daily":"0.5","noise":"47","smart":"미지원","price":"290000"}},
    {"model":"스마트카라 음식물처리기 PCS-600","slug":"smartcara-pcs-600","brand":"스마트카라","category":"food_processor","release_year":"2024","specs":{"brand":"스마트카라","method":"건조분쇄","capacity":"1.0","daily":"0.7","noise":"45","smart":"미지원","price":"499000"}},
    {"model":"루펜 음식물처리기 SLW-02","slug":"loofen-slw-02","brand":"루펜","category":"food_processor","release_year":"2024","specs":{"brand":"루펜","method":"건조","capacity":"2.0","daily":"1.0","noise":"40","smart":"미지원","price":"399000"}},

    # ══════════════════════════════════════════════════════════
    # 카메라
    # ══════════════════════════════════════════════════════════

    {"model":"Sony Alpha 1 II","slug":"sony-alpha-1-ii","brand":"Sony","category":"camera","release_year":"2025","specs":{"brand":"Sony","sensor":"풀프레임 (35mm)","megapixels":"50.1","iso_range":"100-51200","video_max":"8K 30fps / 4K 120fps","af_points":"759","mount":"Sony E 마운트","weight":"743","price":"10000000"}},
    {"model":"Sony A7 V","slug":"sony-a7-v","brand":"Sony","category":"camera","release_year":"2024","specs":{"brand":"Sony","sensor":"풀프레임 (35mm)","megapixels":"61","iso_range":"100-32000","video_max":"4K 60fps","af_points":"693","mount":"Sony E 마운트","weight":"609","price":"4500000"}},
    {"model":"Sony ZV-E10 II","slug":"sony-zv-e10-ii","brand":"Sony","category":"camera","release_year":"2024","specs":{"brand":"Sony","sensor":"APS-C","megapixels":"26","iso_range":"100-51200","video_max":"4K 60fps","af_points":"759","mount":"Sony E 마운트","weight":"291","price":"1099000"}},
    {"model":"Canon EOS R5 Mark II","slug":"canon-eos-r5-mark-ii","brand":"Canon","category":"camera","release_year":"2024","specs":{"brand":"Canon","sensor":"풀프레임 (35mm)","megapixels":"45","iso_range":"100-51200","video_max":"8K 60fps RAW","af_points":"1053","mount":"Canon RF 마운트","weight":"746","price":"5900000"}},
    {"model":"Canon EOS R6 Mark II","slug":"canon-eos-r6-mark-ii","brand":"Canon","category":"camera","release_year":"2023","specs":{"brand":"Canon","sensor":"풀프레임 (35mm)","megapixels":"24.2","iso_range":"100-102400","video_max":"4K 60fps","af_points":"1053","mount":"Canon RF 마운트","weight":"670","price":"3500000"}},
    {"model":"Nikon Z6 III","slug":"nikon-z6-iii","brand":"Nikon","category":"camera","release_year":"2024","specs":{"brand":"Nikon","sensor":"풀프레임 (부분 적층형)","megapixels":"24.5","iso_range":"64-64000","video_max":"6K RAW 60fps / 4K 120fps","af_points":"299","mount":"Nikon Z 마운트","weight":"760","price":"3999000"}},
    {"model":"Fujifilm X-T5","slug":"fujifilm-x-t5","brand":"Fujifilm","category":"camera","release_year":"2023","specs":{"brand":"Fujifilm","sensor":"APS-C (X-Trans 5)","megapixels":"40.2","iso_range":"125-12800","video_max":"6.2K 30fps","af_points":"425","mount":"Fujifilm X 마운트","weight":"557","price":"2299000"}},
    {"model":"Fujifilm X100VI","slug":"fujifilm-x100vi","brand":"Fujifilm","category":"camera","release_year":"2024","specs":{"brand":"Fujifilm","sensor":"APS-C (X-Trans 5)","megapixels":"40.2","iso_range":"125-12800","video_max":"6.2K 30fps","af_points":"425","mount":"고정식 23mm f/2","weight":"521","price":"2099000"}},
    {"model":"GoPro HERO 13 Black","slug":"gopro-hero-13-black","brand":"GoPro","category":"camera","release_year":"2024","specs":{"brand":"GoPro","sensor":"1/1.9인치","megapixels":"27","iso_range":"100-6400","video_max":"5.3K 60fps","af_points":"자동","mount":"GoPro 마운트","weight":"154","price":"599000"}},

    # ══════════════════════════════════════════════════════════
    # 스피커 / 사운드바
    # ══════════════════════════════════════════════════════════

    {"model":"삼성 사운드바 HW-Q990D 11.1.4ch","slug":"samsung-soundbar-hw-q990d","brand":"Samsung","category":"speaker","release_year":"2024","specs":{"brand":"Samsung","type":"사운드바 (서브우퍼+리어 스피커 포함)","channels":"11.1.4","power":"656","surround":"Dolby Atmos, DTS:X","connectivity":"HDMI eARC, Bluetooth, Wi-Fi","price":"1799000"}},
    {"model":"LG 사운드바 S95TR 9.1.5ch","slug":"lg-soundbar-s95tr","brand":"LG","category":"speaker","release_year":"2024","specs":{"brand":"LG","type":"사운드바 (서브우퍼+리어 스피커 포함)","channels":"9.1.5","power":"810","surround":"Dolby Atmos, DTS:X","connectivity":"HDMI eARC, Bluetooth, Wi-Fi","price":"1599000"}},
    {"model":"Sony HT-A9M2","slug":"sony-ht-a9m2","brand":"Sony","category":"speaker","release_year":"2024","specs":{"brand":"Sony","type":"홈시어터 스피커 시스템","channels":"7.1.4","power":"504","surround":"360 Reality Audio, Dolby Atmos, DTS:X","connectivity":"HDMI eARC, Bluetooth, Wi-Fi","price":"2499000"}},
    {"model":"Sonos Arc Ultra","slug":"sonos-arc-ultra","brand":"Sonos","category":"speaker","release_year":"2024","specs":{"brand":"Sonos","type":"사운드바","channels":"9.1.4","power":"0","surround":"Dolby Atmos, DTS:X","connectivity":"HDMI eARC, Wi-Fi, Bluetooth","price":"1299000"}},
    {"model":"Bose Smart Soundbar 900","slug":"bose-smart-soundbar-900","brand":"Bose","category":"speaker","release_year":"2023","specs":{"brand":"Bose","type":"사운드바","channels":"7.1.4","power":"0","surround":"Dolby Atmos, DTS:X","connectivity":"HDMI eARC, Wi-Fi, Bluetooth, AirPlay2","price":"1099000"}},
    {"model":"Marshall Stanmore III","slug":"marshall-stanmore-iii","brand":"Marshall","category":"speaker","release_year":"2023","specs":{"brand":"Marshall","type":"블루투스 스피커","channels":"2.1","power":"80","surround":"스테레오","connectivity":"Bluetooth 5.2, Wi-Fi, 3.5mm","price":"499000"}},

    # ══════════════════════════════════════════════════════════
    # 게임기
    # ══════════════════════════════════════════════════════════

    {"model":"PlayStation 5 Pro","slug":"playstation-5-pro","brand":"Sony","category":"gaming_console","release_year":"2024","specs":{"brand":"Sony","cpu":"AMD Zen 2 (8코어 3.85GHz)","gpu":"AMD RDNA 4 (GPU 45% 향상)","ram":"16","storage":"2","resolution":"8K / 4K 60fps","framerate":"120","optical":"없음 (별도 구매)","price":"1199000"}},
    {"model":"PlayStation 5 Slim (디스크 에디션)","slug":"playstation-5-slim-disc","brand":"Sony","category":"gaming_console","release_year":"2023","specs":{"brand":"Sony","cpu":"AMD Zen 2 (8코어 3.5GHz)","gpu":"AMD RDNA 2 (10.3 TFLOPS)","ram":"16","storage":"1","resolution":"4K 60fps / 8K","framerate":"120","optical":"UHD 블루레이","price":"699000"}},
    {"model":"Xbox Series X","slug":"xbox-series-x","brand":"Microsoft","category":"gaming_console","release_year":"2020","specs":{"brand":"Microsoft","cpu":"AMD Zen 2 (8코어 3.8GHz)","gpu":"AMD RDNA 2 (12 TFLOPS)","ram":"16","storage":"1","resolution":"4K 120fps / 8K","framerate":"120","optical":"UHD 블루레이","price":"699000"}},
    {"model":"Nintendo Switch 2","slug":"nintendo-switch-2","brand":"Nintendo","category":"gaming_console","release_year":"2025","specs":{"brand":"Nintendo","cpu":"NVIDIA Custom (ARM 기반)","gpu":"NVIDIA Custom (DLSS 지원)","ram":"12","storage":"0.256","resolution":"4K (도킹) / 1080p (핸드헬드)","framerate":"120","optical":"없음 (카트리지)","price":"499000"}},
    {"model":"Xbox Series S","slug":"xbox-series-s","brand":"Microsoft","category":"gaming_console","release_year":"2020","specs":{"brand":"Microsoft","cpu":"AMD Zen 2 (8코어 3.6GHz)","gpu":"AMD RDNA 2 (4 TFLOPS)","ram":"10","storage":"0.512","resolution":"1440p 120fps","framerate":"120","optical":"없음","price":"399000"}},
]


# ══════════════════════════════════════════════════════════
# 기술정보 주제 목록
# ══════════════════════════════════════════════════════════

TECH_TOPICS = [
    # 디스플레이
    {"slug":"what-is-refresh-rate",         "title":"주사율(Hz)이란? 60Hz vs 120Hz vs 165Hz 차이 완벽 정리"},
    {"slug":"oled-vs-lcd-vs-amoled",         "title":"OLED vs LCD vs AMOLED 디스플레이 차이점 총정리"},
    {"slug":"what-is-ltpo-display",          "title":"LTPO 디스플레이란? 가변 주사율의 장점과 배터리 효율"},
    {"slug":"what-is-micro-led-display",     "title":"Micro LED 디스플레이란? OLED의 대안이 될 수 있을까?"},
    {"slug":"what-is-dolby-vision",          "title":"돌비 비전(Dolby Vision) vs HDR10+ 차이점 완벽 정리"},
    {"slug":"what-is-nits-brightness",       "title":"밝기 단위 nit이란? 스마트폰 화면 밝기와 야외 가시성"},
    {"slug":"amoled-burn-in-prevention",     "title":"AMOLED 번인 현상이란? 원인과 예방 방법"},
    {"slug":"mini-led-vs-oled-tv",           "title":"Mini LED TV vs OLED TV 차이 — 어떤 걸 선택해야 할까?"},
    {"slug":"tv-refresh-rate-explained",     "title":"TV 주사율 120Hz vs 144Hz — 영화·스포츠 시청 시 체감 차이"},
    # 프로세서 / 메모리
    {"slug":"snapdragon-vs-apple-silicon",   "title":"스마트폰 AP 비교: Snapdragon 8 Elite vs Apple A18 Pro"},
    {"slug":"apple-silicon-m4-explained",    "title":"Apple M4 칩이란? 성능, 효율, 인공지능 처리 능력"},
    {"slug":"ram-vs-storage-difference",     "title":"RAM과 내부저장소 차이점 — 어느 것이 더 중요할까?"},
    {"slug":"lpddr5x-vs-lpddr5",             "title":"LPDDR5X vs LPDDR5 RAM 차이 — 스마트폰 속도에 미치는 영향"},
    {"slug":"what-is-ufs-4-storage",         "title":"UFS 4.0 vs UFS 3.1 스토리지 차이 — 체감 속도는?"},
    {"slug":"ssd-vs-hdd-difference",         "title":"SSD vs HDD 차이점 — NVMe, SATA 종류별 속도 비교"},
    {"slug":"what-is-pcle-5-nvme",           "title":"NVMe PCIe 5.0 SSD란? 속도와 발열 완벽 정리"},
    {"slug":"laptop-tdp-explained",          "title":"노트북 TDP(열설계전력)란? 성능과 발열의 상관관계"},
    {"slug":"laptop-arm-vs-x86",             "title":"ARM vs x86 노트북 차이 — Apple Silicon과 퀄컴 스냅드래곤 X"},
    # 카메라
    {"slug":"smartphone-camera-sensor-size", "title":"스마트폰 카메라 센서 크기가 중요한 이유 — 1인치 센서의 의미"},
    {"slug":"smartphone-periscope-camera",   "title":"페리스코프 망원 카메라란? 광학 줌 5배 10배 원리"},
    {"slug":"how-ai-improves-camera",        "title":"AI가 스마트폰 카메라를 어떻게 개선하는가?"},
    {"slug":"what-is-zeiss-leica-camera",    "title":"스마트폰 카메라 브랜드 협업: ZEISS, Leica, Hasselblad 차이"},
    {"slug":"mirrorless-vs-dslr-2025",       "title":"미러리스 vs DSLR 카메라 — 2025년에도 DSLR을 사야 할까?"},
    {"slug":"camera-sensor-full-frame-apsc", "title":"풀프레임 vs APS-C 센서 차이 — 화질과 가격의 트레이드오프"},
    # 음향
    {"slug":"what-is-anc-noise-cancelling",  "title":"ANC(능동형 소음 제거)란? 원리와 효과적인 사용법"},
    {"slug":"bluetooth-codec-sbc-aac-ldac",  "title":"블루투스 코덱 완전정복: SBC vs AAC vs aptX vs LDAC"},
    {"slug":"what-is-dolby-atmos",           "title":"돌비 애트모스(Dolby Atmos)란? 공간 음향의 원리"},
    {"slug":"what-is-spatial-audio",         "title":"공간 음향(Spatial Audio)이란? 헤드트래킹의 원리"},
    {"slug":"soundbar-vs-home-theater",      "title":"사운드바 vs 홈시어터 — TV 음향 어떤 걸 선택할까?"},
    {"slug":"what-is-pcm-vs-aac-audio",      "title":"스마트폰 음악 품질: 무손실 vs 손실 압축 — 실제로 들릴까?"},
    # 배터리 / 충전
    {"slug":"fast-charging-explained",       "title":"고속충전 기술 총정리: 25W vs 45W vs 100W 차이"},
    {"slug":"battery-mah-vs-real-life",      "title":"배터리 mAh 숫자가 클수록 오래가는 게 맞을까?"},
    {"slug":"wireless-charging-watt-diff",   "title":"무선충전 5W vs 15W vs 50W 차이 — 충전 속도 얼마나 다를까?"},
    {"slug":"ev-charging-type-comparison",   "title":"전기차 충전 방식 완벽 정리: AC 완속 vs DC 급속 vs V2G"},
    # 연결성
    {"slug":"5g-vs-lte-difference",          "title":"5G vs LTE 차이점 — 실생활에서 체감 속도는 얼마나 다를까?"},
    {"slug":"what-is-wi-fi-6e-7",            "title":"Wi-Fi 6E vs Wi-Fi 7 차이 — 어떤 공유기를 골라야 할까?"},
    {"slug":"what-is-usb4-thunderbolt5",     "title":"USB4 vs 썬더볼트 5 차이 — 전송 속도와 활용법"},
    {"slug":"nfc-payments-explained",        "title":"NFC 결제 원리와 삼성페이, 애플페이 차이점"},
    {"slug":"what-is-matter-smart-home",     "title":"Matter 스마트홈 표준이란? 삼성, 애플, 구글 호환 가능?"},
    {"slug":"what-is-wi-fi-calling",         "title":"Wi-Fi 통화(Wi-Fi Calling)란? 지하철에서도 전화 가능할까?"},
    # 스마트홈 / 생활가전
    {"slug":"robot-vacuum-lidar-vs-camera",  "title":"로봇청소기 LiDAR vs 카메라 방식 — 어느 것이 더 잘 피할까?"},
    {"slug":"inverter-ac-vs-non-inverter",   "title":"인버터 에어컨 vs 일반 에어컨 — 전기세 차이 얼마나 날까?"},
    {"slug":"air-purifier-hepa-cadr",        "title":"공기청정기 HEPA 등급과 CADR 수치 — 실제 성능 판단법"},
    {"slug":"drum-vs-agitator-washer",       "title":"드럼 세탁기 vs 통돌이 세탁기 — 세탁력·전기세 비교"},
    {"slug":"refrigerator-inverter-comp",    "title":"냉장고 인버터 컴프레서 — 전기세·소음·수명 차이 정리"},
    {"slug":"energy-grade-explained",        "title":"에너지 소비효율 등급 1등급 vs 5등급 — 연간 전기세 차이"},
    {"slug":"dishwasher-vs-handwashing",     "title":"식기세척기 vs 손설거지 — 전기·물 사용량 어느 쪽이 유리?"},
    {"slug":"air-conditioner-btu-pyeong",    "title":"에어컨 평수 계산법 — BTU와 평형 관계 완벽 정리"},
    # 보안 / 개인정보
    {"slug":"ip68-vs-ip67-waterproof",       "title":"IP68 vs IP67 방수 등급 차이 — 수영장에 넣어도 될까?"},
    {"slug":"in-display-fingerprint-types",  "title":"디스플레이 지문인식 종류 비교: 광학식 vs 초음파식"},
    {"slug":"what-is-gorilla-glass",         "title":"고릴라 글라스 종류별 비교 — Victus 2 vs Victus+ 강도 차이"},
    {"slug":"what-is-satellite-messaging",   "title":"위성 문자 기능이란? iPhone과 Galaxy의 긴급 위성 통신"},
    # 기타 IT
    {"slug":"android-vs-ios-2025",           "title":"2025년 안드로이드 vs iOS 장단점 완벽 비교"},
    {"slug":"foldable-phone-durability",     "title":"폴더블폰 내구성은 괜찮을까? 힌지 수명과 화면 보호"},
    {"slug":"what-is-under-display-camera",  "title":"언더 디스플레이 카메라란? 폴더블폰의 숨겨진 셀카 카메라"},
    {"slug":"smartwatch-gps-types",          "title":"스마트워치 GPS 종류 비교: L1, L5, 듀얼밴드 차이"},
    {"slug":"smartwatch-health-sensors",     "title":"스마트워치 건강 센서 총정리 — 심전도, 혈압, 혈중산소 측정 원리"},
    {"slug":"gaming-console-ssd-speed",      "title":"PS5·Xbox Series X SSD가 왜 중요한가? 로딩 속도 혁신"},
    {"slug":"how-to-read-benchmark-scores",  "title":"AnTuTu, Geekbench 벤치마크 점수 읽는 법"},
    {"slug":"what-is-find-my-network",       "title":"분실 추적 기술 비교: Apple AirTag vs Samsung SmartTag vs Tile"},
    {"slug":"laptop-gpu-integrated-vs-discrete","title":"내장 GPU vs 외장 GPU — 노트북 선택 시 고려할 점"},
    {"slug":"tablet-vs-laptop-productivity", "title":"태블릿 vs 노트북 생산성 비교 — 어떤 걸 사야 할까?"},

    # ── 스마트폰 가이드
    {"slug":"smartphone-buying-guide",           "title":"스마트폰 구매 가이드 완전 정복 — 스펙 보는 법부터 예산 설정까지"},
    {"slug":"smartphone-camera-spec-guide",      "title":"스마트폰 카메라 스펙 해설 — 화소수보다 중요한 것들"},
    {"slug":"smartphone-battery-tips",           "title":"스마트폰 배터리 오래 쓰는 법 — 충전 습관부터 절전 설정까지"},
    {"slug":"smartphone-used-buying-checklist",  "title":"중고 스마트폰 구매 전 반드시 확인해야 할 10가지"},
    {"slug":"smartphone-as-comparison",          "title":"스마트폰 브랜드별 A/S 비교 — 삼성·애플·샤오미 서비스 차이"},
    {"slug":"smartphone-5g-worth-it",            "title":"5G 스마트폰 지금 사야 할까? 실생활 체감 차이 정리"},
    {"slug":"smartphone-chip-performance",       "title":"스마트폰 AP 성능 비교 — 스냅드래곤·엑시노스·Tensor 실차이"},
    {"slug":"smartphone-repair-cost-saving",     "title":"스마트폰 수리비 절약하는 법 — 보험·공식 수리·자가수리 비교"},

    # ── 노트북 가이드
    {"slug":"laptop-buying-guide",               "title":"노트북 구매 가이드 2026 — 용도별 추천 스펙 완전 정복"},
    {"slug":"laptop-cpu-gpu-guide",              "title":"노트북 CPU vs GPU 선택 기준 — 영상 편집·게임·사무용 차이"},
    {"slug":"macbook-vs-windows-laptop",         "title":"맥북 vs 윈도우 노트북 비교 — 2026년 어느 쪽이 맞을까?"},
    {"slug":"laptop-battery-life-tips",          "title":"노트북 배터리 수명 늘리는 방법 — 충전 패턴과 설정 최적화"},
    {"slug":"laptop-display-resolution-guide",   "title":"노트북 디스플레이 해상도 차이 — FHD vs QHD vs 4K 실체감"},
    {"slug":"gaming-vs-regular-laptop",          "title":"게이밍 노트북 vs 일반 노트북 — 일상에서 게이밍 노트북 써도 될까?"},
    {"slug":"laptop-ram-guide",                  "title":"노트북 RAM 용량 얼마가 적당한가 — 8GB·16GB·32GB 용도별 정리"},
    {"slug":"laptop-ports-guide",                "title":"노트북 포트 종류 완전 정리 — USB-A·C·HDMI·SD카드 활용법"},
    {"slug":"laptop-wfh-selection-guide",        "title":"재택근무용 노트북 추천 기준 — 화상회의·문서 작업 최적 스펙"},

    # ── 태블릿 가이드
    {"slug":"tablet-buying-guide",               "title":"태블릿 구매 가이드 — 용도별 추천 모델과 스펙 체크포인트"},
    {"slug":"ipad-vs-galaxy-tab",                "title":"아이패드 vs 갤럭시탭 비교 — 2026년 어느 쪽이 더 나을까?"},
    {"slug":"tablet-stylus-comparison",          "title":"태블릿 스타일러스 비교 — 애플 펜슬 vs S펜 vs 서드파티"},
    {"slug":"tablet-display-size-guide",         "title":"태블릿 디스플레이 크기 선택법 — 10·11·13인치 용도별 차이"},
    {"slug":"tablet-student-guide",              "title":"학생용 태블릿 선택 가이드 — 필기·강의 녹음·PDF 활용 최적 모델"},
    {"slug":"tablet-keyboard-cover-guide",       "title":"태블릿 키보드 커버 선택법 — 공식 vs 서드파티 비교"},
    {"slug":"tablet-battery-management",         "title":"태블릿 배터리 관리 완전 정복 — 장기간 보관·충전 방법"},

    # ── 이어폰·헤드폰 가이드
    {"slug":"earphone-buying-guide",             "title":"이어폰·헤드폰 구매 가이드 — 인이어·오버이어 용도별 선택법"},
    {"slug":"wired-vs-wireless-earphone",        "title":"유선 vs 무선 이어폰 장단점 — 음질·편의성·가격 비교"},
    {"slug":"earphone-driver-types",             "title":"이어폰 드라이버 종류 해설 — 다이나믹·BA·평판형 차이"},
    {"slug":"earphone-type-comparison",          "title":"인이어 vs 온이어 vs 오버이어 — 착용감·음질·용도 비교"},
    {"slug":"earphone-sound-quality-tips",       "title":"이어폰 음질 개선하는 팁 — 이퀄라이저 설정과 팁 교체 효과"},
    {"slug":"earphone-maintenance",              "title":"이어폰 관리법 완전 정복 — 보관·세척·케이블 수명 늘리기"},

    # ── 스마트워치 가이드
    {"slug":"smartwatch-buying-guide",           "title":"스마트워치 구매 가이드 — 건강·운동·알림 용도별 선택법"},
    {"slug":"apple-watch-vs-galaxy-watch",       "title":"애플워치 vs 갤럭시워치 비교 — 2026년 어느 쪽이 더 나을까?"},
    {"slug":"smartwatch-health-accuracy",        "title":"스마트워치 건강 측정 정확도 — 심박수·혈압·혈중산소 실제 오차"},
    {"slug":"smartwatch-battery-comparison",     "title":"스마트워치 배터리 비교 — 1일 vs 1주일 어느 쪽이 실용적?"},
    {"slug":"smartwatch-fitness-tracking",       "title":"스마트워치 운동 추적 기능 비교 — GPS·심박·수면 분석 정확도"},
    {"slug":"smartwatch-compatibility-guide",    "title":"스마트워치 호환성 확인 방법 — iOS·안드로이드 기기별 제약"},

    # ── TV 가이드
    {"slug":"tv-buying-guide",                   "title":"TV 구매 가이드 완전 정복 — 화질·인치·예산별 선택 기준"},
    {"slug":"tv-size-selection-guide",           "title":"TV 인치 크기 선택 가이드 — 시청 거리별 최적 화면 크기"},
    {"slug":"gaming-tv-guide",                   "title":"게이밍 TV 선택 기준 — HDMI 2.1·120Hz·VRR 반드시 확인"},
    {"slug":"tv-picture-mode-settings",          "title":"TV 화질 모드 설정 최적화 — 영화·스포츠·게임별 추천 설정"},
    {"slug":"smart-tv-platform-comparison",      "title":"스마트TV 플랫폼 비교 — 타이젠·webOS·구글TV 차이점"},
    {"slug":"tv-soundbar-guide",                 "title":"TV 사운드바 선택법 — 2.0·2.1·5.1채널 예산별 추천"},
    {"slug":"tv-energy-efficiency",              "title":"TV 에너지 효율 비교 — OLED·QLED·LCD 연간 전기세 차이"},
    {"slug":"tv-anti-glare-guide",               "title":"TV 반사 방지 처리 비교 — 무광·유광 패널 거실 환경별 선택"},

    # ── 모니터 가이드
    {"slug":"monitor-buying-guide",              "title":"모니터 구매 가이드 — 용도별 추천 스펙과 예산 설정"},
    {"slug":"gaming-vs-office-monitor",          "title":"게이밍 모니터 vs 업무용 모니터 — 색정확도·주사율 우선순위"},
    {"slug":"monitor-panel-comparison",          "title":"모니터 패널 IPS vs VA vs TN 비교 — 용도별 최선의 선택"},
    {"slug":"monitor-refresh-rate-guide",        "title":"모니터 주사율 60·144·240Hz 차이 — 게임별 체감 차이 정리"},
    {"slug":"monitor-resolution-comparison",     "title":"모니터 해상도 FHD vs QHD vs 4K — GPU 부하와 화질 트레이드오프"},
    {"slug":"ultrawide-monitor-guide",           "title":"울트라와이드 모니터 장단점 — 생산성과 게임 어느 쪽에 유리?"},
    {"slug":"monitor-color-accuracy",            "title":"모니터 색재현율 sRGB vs DCI-P3 — 디자이너·영상 편집자 선택법"},
    {"slug":"dual-monitor-setup-guide",          "title":"듀얼 모니터 세팅 가이드 — 배치·설정·생산성 향상 방법"},

    # ── 카메라 가이드
    {"slug":"camera-buying-guide",               "title":"카메라 구매 가이드 완전 정복 — 입문자부터 중급자까지"},
    {"slug":"camera-lens-beginner-guide",        "title":"카메라 렌즈 선택 입문 가이드 — 화각·밝기·용도별 추천"},
    {"slug":"camera-af-comparison",              "title":"카메라 AF 시스템 비교 — 위상차·콘트라스트·하이브리드 차이"},
    {"slug":"action-cam-comparison",             "title":"액션캠 비교 — 고프로·DJI·소니 어느 쪽이 나을까?"},
    {"slug":"camera-stabilization-guide",        "title":"카메라 손떨림 보정 OIS vs IBIS 차이 — 영상 촬영 체감 효과"},
    {"slug":"camera-video-spec-guide",           "title":"카메라 동영상 스펙 해설 — 4K·8K·ProRes·Log 촬영 차이"},

    # ── 스피커 가이드
    {"slug":"speaker-buying-guide",              "title":"스피커 구매 가이드 — 블루투스·유선·사운드바 용도별 선택"},
    {"slug":"soundbar-vs-multichannel",          "title":"사운드바 vs 2.1ch vs 5.1ch 비교 — 공간·예산별 최선의 선택"},
    {"slug":"speaker-ip-rating-guide",           "title":"블루투스 스피커 방수 등급 — IP67·IP68·IPX7 차이와 활용"},
    {"slug":"speaker-room-setup",                "title":"스피커 공간 최적화 세팅법 — 위치·방향·흡음재 배치 가이드"},
    {"slug":"multiroom-audio-guide",             "title":"무선 멀티룸 오디오 가이드 — 소노스·WiSA·에어플레이 비교"},
    {"slug":"speaker-frequency-response",        "title":"스피커 주파수 응답 특성 해설 — 저음·중음·고음 스펙 읽는 법"},

    # ── 게임기 가이드
    {"slug":"gaming-console-buying-guide",       "title":"게임기 구매 가이드 — PS5·Xbox·스위치 용도별 선택"},
    {"slug":"console-comparison",                "title":"PS5 vs Xbox Series X vs 닌텐도 스위치 2 완전 비교"},
    {"slug":"console-ssd-upgrade",               "title":"게임기 SSD 업그레이드 가이드 — PS5·Xbox 용량 확장 방법"},
    {"slug":"console-disc-vs-digital",           "title":"게임기 디스크 vs 디지털 에디션 — 장기적으로 어느 쪽이 유리?"},
    {"slug":"gaming-subscription-comparison",    "title":"게임 구독 서비스 비교 — PS Plus·Game Pass·닌텐도 온라인"},
    {"slug":"gaming-peripherals-guide",          "title":"게이밍 주변기기 선택 가이드 — 컨트롤러·헤드셋·거치대"},

    # ── 냉장고 가이드
    {"slug":"refrigerator-buying-guide",         "title":"냉장고 구매 가이드 완전 정복 — 용량·종류·예산별 선택법"},
    {"slug":"refrigerator-type-comparison",      "title":"양문형 vs 4도어 vs 일반 냉장고 비교 — 가족 수별 추천"},
    {"slug":"refrigerator-capacity-guide",       "title":"냉장고 용량 선택 가이드 — 1인·2인·4인 가구별 적정 L"},
    {"slug":"refrigerator-energy-grade",         "title":"냉장고 에너지 효율 등급 해설 — 연간 전기세 얼마나 차이날까?"},
    {"slug":"refrigerator-organization-tips",    "title":"냉장고 수납 정리 최적화 팁 — 식품별 보관 위치와 온도 구역"},
    {"slug":"refrigerator-noise-reduction",      "title":"냉장고 소음 원인과 줄이는 방법 — dB 기준 조용한 모델 선택"},
    {"slug":"refrigerator-as-comparison",        "title":"냉장고 A/S 비교 — 삼성·LG·위니아 출장비·부품비 차이"},
    {"slug":"kimchi-refrigerator-comparison",    "title":"김치냉장고 vs 일반 냉장고 김치칸 차이 — 따로 사야 할까?"},

    # ── 세탁기 가이드
    {"slug":"washing-machine-buying-guide",      "title":"세탁기 구매 가이드 — 드럼·통돌이·용량별 선택 기준"},
    {"slug":"washing-machine-capacity-guide",    "title":"세탁기 용량 선택 기준 — 가족 수별 적정 kg 완전 정리"},
    {"slug":"washing-machine-energy-tips",       "title":"세탁기 전기세·물세 절약 팁 — 세탁 온도·코스별 에너지 비교"},
    {"slug":"washing-machine-maintenance",       "title":"세탁기 청소 및 관리법 — 드럼 세척·필터 청소 주기 가이드"},
    {"slug":"washer-dryer-combo-guide",          "title":"세탁건조기 겸용 vs 분리형 — 공간·성능·비용 완전 비교"},
    {"slug":"washing-machine-program-guide",     "title":"세탁기 코스별 사용 가이드 — 울·쾌속·표준 코스 언제 써야?"},

    # ── 에어컨 가이드
    {"slug":"air-conditioner-buying-guide",      "title":"에어컨 구매 가이드 — 평수·효율·설치 방식별 선택법"},
    {"slug":"ac-room-size-guide",                "title":"에어컨 평수 선택 기준 — 방 크기와 냉방 능력 매칭 방법"},
    {"slug":"ac-cleaning-guide",                 "title":"에어컨 청소 방법 완전 가이드 — 필터·열교환기·자가 청소 주기"},
    {"slug":"ac-efficiency-tips",                "title":"에어컨 냉방 효율 높이는 팁 — 온도 설정·습도·바람 방향 조절"},
    {"slug":"portable-vs-window-ac",             "title":"이동식 에어컨 vs 창문형 에어컨 비교 — 설치·효율·소음 차이"},
    {"slug":"ac-brand-comparison",               "title":"에어컨 브랜드 비교 — 삼성·LG·다이킨 효율·A/S·가격 차이"},

    # ── 공기청정기 가이드
    {"slug":"air-purifier-buying-guide",         "title":"공기청정기 구매 가이드 — 면적·필터·소음별 선택 기준"},
    {"slug":"hepa-filter-guide",                 "title":"HEPA 필터 종류와 등급 완전 해설 — H13 vs H14 차이"},
    {"slug":"air-purifier-coverage-guide",       "title":"공기청정기 면적 선택 기준 — CADR 수치와 방 크기 관계"},
    {"slug":"air-purifier-filter-maintenance",   "title":"공기청정기 필터 교체 주기와 비용 — 브랜드별 소모품 비교"},
    {"slug":"air-purifier-noise-comparison",     "title":"공기청정기 소음 비교 — 취침 모드 dB 기준 조용한 모델 선택"},
    {"slug":"air-purifier-humidifier-combo",     "title":"가습 공기청정기 장단점 — 가습 기능이 정말 도움이 될까?"},

    # ── 로봇청소기 가이드
    {"slug":"robot-vacuum-buying-guide",         "title":"로봇청소기 구매 가이드 — LiDAR·카메라·흡입력별 선택법"},
    {"slug":"robot-vacuum-suction-guide",        "title":"로봇청소기 흡입력 Pa 단위 해설 — 수치가 높을수록 좋을까?"},
    {"slug":"robot-vacuum-obstacle-avoidance",   "title":"로봇청소기 장애물 인식 기술 비교 — LiDAR vs 3D 구조광"},
    {"slug":"robot-vacuum-mop-comparison",       "title":"로봇청소기 물걸레 기능 비교 — 진동·회전·리프팅 방식 차이"},
    {"slug":"robot-vacuum-auto-empty",           "title":"로봇청소기 자동 비움 스테이션 — 집진 용량·청소 주기 완전 정리"},
    {"slug":"robot-vacuum-pet-guide",            "title":"반려동물 가정 로봇청소기 선택법 — 털 막힘·배변 감지 기능 비교"},

    # ── 청소기 가이드
    {"slug":"vacuum-buying-guide",               "title":"무선 청소기 구매 가이드 — 흡입력·배터리·헤드별 선택 기준"},
    {"slug":"dyson-vs-samsung-vacuum",           "title":"다이슨 vs 삼성 무선청소기 비교 — 흡입력·무게·가격 실차이"},
    {"slug":"vacuum-suction-units",              "title":"청소기 흡입력 W vs Pa vs AW — 단위 비교와 실사용 성능"},
    {"slug":"vacuum-battery-guide",              "title":"청소기 배터리 교체형 vs 일체형 — 장기 비용과 편의성 비교"},
    {"slug":"vacuum-filter-maintenance",         "title":"청소기 필터 관리 완전 정복 — 세척·교체 주기 브랜드별 차이"},
    {"slug":"vacuum-head-types",                 "title":"청소기 헤드 종류와 용도 — 바닥·침구·틈새 노즐 활용법"},

    # ── 전자레인지 가이드
    {"slug":"microwave-buying-guide",            "title":"전자레인지 구매 가이드 — 용량·출력·기능별 선택 기준"},
    {"slug":"microwave-vs-airfryer-vs-oven",     "title":"전자레인지 vs 에어프라이어 vs 오븐 — 요리별 최적 기기"},
    {"slug":"inverter-microwave-technology",     "title":"인버터 전자레인지 기술 해설 — 일반 전자레인지와 차이점"},
    {"slug":"microwave-capacity-guide",          "title":"전자레인지 용량 선택 기준 — 1인·4인 가구별 적정 L"},
    {"slug":"microwave-cleaning-guide",          "title":"전자레인지 청소 및 냄새 제거법 — 레몬·식초 활용 완전 정복"},
    {"slug":"microwave-grill-guide",             "title":"그릴 전자레인지 기능 완전 정복 — 굽기·스팀·에어프라이 활용"},

    # ── 헤어드라이어 가이드
    {"slug":"hair-dryer-buying-guide",           "title":"헤어드라이어 구매 가이드 — 와트·이온·열 보호 기능별 선택"},
    {"slug":"dyson-hair-dryer-comparison",       "title":"다이슨 헤어드라이어 vs 일반 제품 비교 — 가격 차이 정말 값어치?"},
    {"slug":"hair-dryer-wattage-guide",          "title":"헤어드라이어 와트 선택 기준 — 1200W·1800W·2400W 차이"},
    {"slug":"ionic-hair-dryer-guide",            "title":"이온 기술 헤어드라이어 효과 — 실제로 모발 손상이 줄어들까?"},
    {"slug":"hair-dryer-attachments",            "title":"헤어드라이어 노즐·디퓨저 종류와 용도 — 헤어스타일별 선택"},
    {"slug":"hair-dryer-usage-tips",             "title":"헤어드라이어 올바른 사용법 — 거리·온도·방향 모발 손상 최소화"},

    # ── 전기면도기 가이드
    {"slug":"electric-shaver-buying-guide",      "title":"전기면도기 구매 가이드 — 왕복식·회전식·예산별 선택법"},
    {"slug":"rotary-vs-foil-shaver",             "title":"왕복식 vs 회전식 면도기 비교 — 피부 타입별 어느 쪽이 나을까?"},
    {"slug":"shaver-waterproof-guide",           "title":"전기면도기 방수 등급 완전 해설 — 세면대·샤워 중 사용 가능?"},
    {"slug":"shaver-blade-replacement",          "title":"전기면도기 날 교체 주기와 비용 — 브랜드별 소모품 가격 비교"},
    {"slug":"wet-vs-dry-shaving",                "title":"습식 vs 건식 면도 비교 — 피부 자극·편의성 실생활 차이"},
    {"slug":"shaver-cleaning-guide",             "title":"전기면도기 세척 방법 완전 정복 — 자동 세척 스테이션 필요한가?"},

    # ── 음식물처리기 가이드
    {"slug":"food-processor-buying-guide",       "title":"음식물처리기 구매 가이드 — 건식·습식·미생물 방식 비교"},
    {"slug":"food-processor-dry-vs-wet",         "title":"음식물처리기 건식 vs 습식 비교 — 처리 속도·냄새·비용 차이"},
    {"slug":"food-processor-capacity-guide",     "title":"음식물처리기 용량과 가족 수 기준 — 얼마짜리가 적당할까?"},
    {"slug":"food-processor-odor-management",    "title":"음식물처리기 냄새 관리 완전 정복 — 설치 위치·환기 방법"},
    {"slug":"food-processor-electricity-cost",   "title":"음식물처리기 전기요금 계산법 — 월 사용 비용 브랜드별 비교"},
    {"slug":"food-processor-installation",       "title":"음식물처리기 설치 조건과 공간 요구사항 — 셀프 설치 가능한가?"},

    # ── 디스플레이 기술
    {"slug":"qd-oled-technology",                "title":"QD-OLED 기술 완전 해설 — 삼성 양자점 OLED의 원리와 장점"},
    {"slug":"hdr-standard-comparison",           "title":"HDR10 vs Dolby Vision vs HDR10+ 완전 비교 — 어느 쪽이 우세?"},
    {"slug":"display-brightness-nits",           "title":"디스플레이 밝기 단위 nit 완전 이해 — 2000nit가 1000nit보다 좋을까?"},
    {"slug":"ltpo-variable-refresh-rate",        "title":"LTPO 가변 주사율 기술 해설 — 1Hz~120Hz 배터리 절약 원리"},
    {"slug":"display-color-gamut",               "title":"디스플레이 색재현율 완전 정복 — sRGB·DCI-P3·Adobe RGB 차이"},
    {"slug":"oled-burn-in-prevention",           "title":"OLED 번인 방지 완전 가이드 — TV·스마트폰·모니터 관리법"},
    {"slug":"touchscreen-technology",            "title":"터치스크린 기술 해설 — 정전용량식·압저항식·초음파식 차이"},
    {"slug":"foldable-display-technology",       "title":"폴더블 디스플레이 기술과 내구성 — UTG 유리와 힌지 구조 해설"},
    {"slug":"display-response-time",             "title":"모니터 응답 속도 ms 완전 해설 — 1ms vs 4ms 게임 체감 차이"},
    {"slug":"local-dimming-technology",          "title":"로컬 디밍 기술 해설 — FALD·엣지형 차이와 명암비 영향"},

    # ── 프로세서·메모리 기술
    {"slug":"mobile-gpu-guide",                  "title":"모바일 GPU 성능 비교 — 아드레노·말리·파워VR 차이 해설"},
    {"slug":"semiconductor-process-node",        "title":"반도체 공정 3nm·4nm·5nm 완전 해설 — 숫자가 작을수록 좋은 이유"},
    {"slug":"npu-ai-chip-guide",                 "title":"NPU와 온디바이스 AI — 갤럭시·아이폰의 AI 처리 방식 차이"},
    {"slug":"benchmark-interpretation-guide",    "title":"벤치마크 점수 해석 방법 — AnTuTu·긱벤치·3DMark 실제 의미"},
    {"slug":"chip-thermal-management",           "title":"스마트폰 칩 발열 관리 기술 — 쿨링 시스템과 성능 유지 방법"},
    {"slug":"intel-vs-amd-laptop",               "title":"인텔 vs AMD 노트북 CPU 비교 — 성능·배터리·호환성 실차이"},
    {"slug":"lpddr5x-memory-guide",              "title":"LPDDR5X 메모리 완전 가이드 — 스마트폰·노트북 속도 영향"},
    {"slug":"cache-memory-explained",            "title":"CPU 캐시 메모리란? L1·L2·L3 캐시 성능 차이 해설"},

    # ── 배터리·충전 기술
    {"slug":"battery-capacity-guide",            "title":"배터리 mAh와 실사용 시간 관계 — 다른 기기 비교 방법"},
    {"slug":"usb-pd-charging-guide",             "title":"USB PD 충전 규격 완전 정복 — 20W·45W·100W 선택법"},
    {"slug":"reverse-wireless-charging",         "title":"역방향 무선충전 기술 해설 — 스마트폰으로 이어폰 충전 원리"},
    {"slug":"battery-cycle-life-guide",          "title":"배터리 사이클 수명 완전 이해 — 몇 번 충전하면 교체해야 할까?"},
    {"slug":"battery-health-check",              "title":"스마트폰·노트북 배터리 건강 확인 방법 — 교체 시점 판단법"},
    {"slug":"gan-charger-explained",             "title":"GaN 충전기란? 질화갈륨 기술과 기존 충전기 차이점"},
    {"slug":"solar-charging-gadgets",            "title":"태양광 충전 기기 완전 가이드 — 스마트폰·캠핑용 솔라 패널 선택"},

    # ── 연결성 기술
    {"slug":"wifi-7-technology-guide",           "title":"Wi-Fi 7 기술 완전 해설 — MLO·320MHz 대역폭 실제 체감"},
    {"slug":"bluetooth-technology-guide",        "title":"블루투스 5.4 기술과 제품 적용 — LE Audio·LC3 코덱 해설"},
    {"slug":"5g-band-comparison",                "title":"5G mmWave vs Sub-6GHz 차이 — 한국에서 실제로 쓰는 5G는?"},
    {"slug":"usb4-thunderbolt4-guide",           "title":"USB4 vs 썬더볼트 4 완전 비교 — 속도·호환성·케이블 선택"},
    {"slug":"hdmi-vs-displayport",               "title":"HDMI 2.1 vs DisplayPort 2.1 비교 — 게이밍·4K 어느 쪽이 유리?"},
    {"slug":"nfc-technology-guide",              "title":"NFC 기술 활용 완전 가이드 — 결제·교통카드·스마트태그 사용법"},
    {"slug":"uwb-technology-guide",              "title":"UWB 초광대역 기술 해설 — 정밀 위치 추적과 스마트홈 활용"},
    {"slug":"satellite-communication-phones",    "title":"위성통신 스마트폰 탑재 기술 — 긴급 SOS와 위성 인터넷 차이"},

    # ── 오디오 기술
    {"slug":"spatial-audio-guide",               "title":"공간 음향 완전 가이드 — 돌비 애트모스·소니 360 Reality Audio 차이"},
    {"slug":"speaker-impedance-guide",           "title":"스피커 임피던스 Ω 완전 해설 — 4옴·8옴 앰프 매칭 방법"},
    {"slug":"hifi-audio-beginner",               "title":"Hi-Fi 오디오 입문 가이드 — DAC·앰프·스피커 시스템 구성법"},
    {"slug":"microphone-types-guide",            "title":"마이크 지향성 완전 해설 — 단일·양방향·무지향 방송·회의별 선택"},
    {"slug":"dac-amp-beginner-guide",            "title":"DAC·AMP 오디오 기기 입문 — 스마트폰 음질 개선 효과 있을까?"},
    {"slug":"lossless-audio-streaming",          "title":"무손실 음원 스트리밍 가이드 — 애플 뮤직·타이달 실제 음질 차이"},

    # ── 카메라 기술
    {"slug":"computational-photography",         "title":"컴퓨테이셔널 포토그래피 완전 해설 — AI가 스마트폰 사진을 바꾼 방식"},
    {"slug":"raw-vs-jpeg-photography",           "title":"RAW vs JPEG 촬영 완전 비교 — 후보정 품질과 용량 트레이드오프"},
    {"slug":"night-mode-photography-guide",      "title":"야간 촬영 기술 해설 — 나이트 모드 멀티프레임 합성 원리"},
    {"slug":"camera-aperture-guide",             "title":"카메라 조리개 F값 완전 해설 — 심도·밝기·보케 관계 정리"},
    {"slug":"video-codec-comparison",            "title":"동영상 코덱 비교 — H.264·H.265·AV1·ProRes 용도별 선택"},
    {"slug":"ois-vs-eis-stabilization",          "title":"OIS vs EIS 손떨림 보정 비교 — 광학과 전자식 실효 차이"},

    # ── 스마트홈 · IoT
    {"slug":"smart-home-beginner-guide",         "title":"스마트홈 입문 가이드 — 허브·플랫폼·기기 구성 시작 방법"},
    {"slug":"smart-home-platform-comparison",    "title":"스마트홈 플랫폼 비교 — 구글홈·애플홈·삼성 스마트싱스 차이"},
    {"slug":"smart-lighting-guide",              "title":"스마트 조명 선택 및 설치 — 필립스 휴·나눔·시라이트 비교"},
    {"slug":"home-security-camera-guide",        "title":"홈 CCTV 보안 카메라 선택법 — 실내·실외·AI 감지 기능 비교"},
    {"slug":"nas-home-server-guide",             "title":"NAS 홈서버 입문 가이드 — 사진 백업·미디어 서버 구성법"},
    {"slug":"smart-plug-guide",                  "title":"스마트 플러그 활용법 — 전력 모니터링·자동화 루틴 설정"},
    {"slug":"smart-home-energy-saving",          "title":"스마트홈 에너지 절약 자동화 — 전기세 줄이는 루틴 설정법"},
    {"slug":"matter-protocol-deep-dive",         "title":"Matter 프로토콜 완전 해설 — Thread·Zigbee·Z-Wave 어떻게 다른가?"},

    # ── 보안 · 개인정보
    {"slug":"biometric-security-comparison",     "title":"스마트폰 생체인식 보안 비교 — 지문·홍채·안면인식 안전성"},
    {"slug":"encryption-technology-guide",       "title":"암호화 기술 완전 이해 — AES·RSA·종단간 암호화 쉽게 설명"},
    {"slug":"two-factor-authentication-guide",   "title":"이중인증 2FA 완전 가이드 — SMS·앱·하드웨어 키 어느 쪽이 안전?"},
    {"slug":"privacy-settings-guide",            "title":"스마트폰 개인정보 보호 설정 완전 정복 — 안드로이드·iOS 비교"},
    {"slug":"vpn-guide",                         "title":"VPN 사용 이유와 선택 방법 — 유료 vs 무료 VPN 실차이"},
    {"slug":"password-manager-guide",            "title":"비밀번호 관리자 사용 가이드 — 1Password·비트워든·삼성패스 비교"},

    # ── 친환경 · 에너지
    {"slug":"energy-efficiency-rating-guide",    "title":"전자기기 에너지 소비효율 등급 완전 해설 — 연간 비용 계산법"},
    {"slug":"e-waste-disposal-guide",            "title":"전자폐기물 올바른 처리 방법 — 공식 수거 채널과 개인정보 삭제"},
    {"slug":"recycled-materials-electronics",    "title":"재활용 소재 전자기기 트렌드 — 바다 플라스틱·재생 알루미늄 적용"},
    {"slug":"power-saving-mode-guide",           "title":"절전 모드 설정으로 전기요금 줄이기 — TV·에어컨·냉장고 설정"},
    {"slug":"electronics-carbon-footprint",      "title":"전자기기 탄소발자국 — 스마트폰 하나 만드는 데 CO2 얼마나?"},
    {"slug":"energy-star-certification",         "title":"에너지 스타 인증 완전 정복 — 가전 구매 시 인증 마크 의미"},

    # ── 수리 · 유지보수
    {"slug":"repairability-score-guide",         "title":"전자기기 수리가능성 점수 해설 — iFixit 점수와 제품 수명"},
    {"slug":"warranty-as-guide",                 "title":"전자기기 보증 기간과 A/S 비교 — 제조사 보증 vs 확장 보증"},
    {"slug":"used-electronics-buying-guide",     "title":"중고 전자기기 구매 완전 가이드 — 사기 예방과 상태 확인법"},
    {"slug":"electronics-insurance-comparison",  "title":"전자기기 보험 서비스 비교 — 제조사·통신사·사설 보험 차이"},
    {"slug":"diy-repair-beginner-guide",         "title":"스마트폰 자가수리 입문 가이드 — 배터리·화면 교체 시작법"},
    {"slug":"dust-proof-care-guide",             "title":"전자기기 먼지 방지와 관리법 — 통풍구 청소·보관 방법 정리"},

    # ── AI · 소프트웨어
    {"slug":"on-device-vs-cloud-ai",             "title":"온디바이스 AI vs 클라우드 AI 차이 — 속도·프라이버시·비용 비교"},
    {"slug":"generative-ai-smartphone",          "title":"생성형 AI 스마트폰 기능 완전 정복 — 갤럭시 AI·애플 인텔리전스"},
    {"slug":"ai-translation-comparison",         "title":"AI 번역 기능 비교 — 통역 이어폰·스마트폰 실시간 번역 성능"},
    {"slug":"ai-assistant-comparison",           "title":"AI 어시스턴트 비교 — 빅스비·시리·구글 어시스턴트·챗GPT 차이"},
    {"slug":"ai-photo-editing-features",         "title":"AI 카메라 편집 기능 완전 정복 — 지우기·배경 교체·생성 채우기"},
    {"slug":"os-update-policy-comparison",       "title":"운영체제 업데이트 정책 비교 — 삼성·애플·구글 지원 기간"},
    {"slug":"android-vs-ios-ecosystem",          "title":"안드로이드 vs iOS 생태계 비교 — 앱·기기 연동·보안 2026 기준"},
    {"slug":"cloud-storage-comparison",          "title":"클라우드 스토리지 서비스 비교 — 구글드라이브·아이클라우드·원드라이브"},
]


def get_products_by_category(category: str) -> list:
    return [p for p in PRODUCTS if p["category"] == category]


def get_product_by_slug(slug: str) -> dict | None:
    return next((p for p in PRODUCTS if p["slug"] == slug), None)
