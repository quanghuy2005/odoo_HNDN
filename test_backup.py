try:
    doc = env['tai_lieu.ke_toa'].search([('ma_tai_lieu', '=', 'TD/2026/03/0001')], limit=1)
    print(f"Doc found: {doc}")
    print(f"Files: {doc.danh_sach_file_dinh_kem}")
    
    cfg = env['google.drive.integration'].search([], limit=1)
    print(f"Config bat_backup: {cfg.bat_backup}, backup_khi_hoan_tat: {cfg.backup_khi_hoan_tat}")
    
    for f in doc.danh_sach_file_dinh_kem:
        print(f"File name: {f.ten_file}, Content logic: {bool(f.file_noi_dung)}")
        
    doc._backup_to_google_drive(event='hoan_tat')
    env.cr.commit()
    print("Done")
except Exception as e:
    import traceback
    traceback.print_exc()
