# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
import io

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleDriveIntegration(models.Model):
    """Tích hợp Google Drive để backup tài liệu"""
    _name = 'google.drive.integration'
    _description = 'Cấu Hình Google Drive'
    _rec_name = 'ten_config'

    ten_config = fields.Char(
        string='Tên Cấu Hình',
        required=True,
        default='Google Drive Backup'
    )

    service_account_json = fields.Text(
        string='Service Account JSON',
        help='Dán nội dung file JSON từ Google Cloud Console'
    )

    thu_muc_cha_id = fields.Char(
        string='Folder ID (Google Drive)',
        required=True,
        help='ID của folder trên Google Drive. Lấy từ URL: https://drive.google.com/drive/folders/[ID]'
    )

    bat_backup = fields.Boolean(
        string='Bật Backup Tự Động',
        default=True
    )

    backup_khi_tao = fields.Boolean(
        string='Backup Khi Tạo',
        default=True
    )

    backup_khi_phe_duyet = fields.Boolean(
        string='Backup Khi Phê Duyệt',
        default=True
    )

    backup_khi_ky = fields.Boolean(
        string='Backup Khi Ký',
        default=True
    )

    backup_khi_hoan_tat = fields.Boolean(
        string='Backup Khi Hoàn Tất',
        default=True
    )

    def _get_drive_service(self):
        """Lấy service Google Drive"""
        if not GOOGLE_AVAILABLE:
            raise UserError(
                'Cần cài đặt: pip install google-auth-httplib2 google-auth-oauthlib google-api-python-client'
            )

        try:
            import json
            credentials_dict = json.loads(self.service_account_json)
            credentials = Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            raise UserError(f'Lỗi xác thực Google: {str(e)}')

    def test_connection(self):
        """Test kết nối Google Drive"""
        try:
            service = self._get_drive_service()
            folder_id = self.thu_muc_cha_id.strip() if self.thu_muc_cha_id else ''
            results = service.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                pageSize=1,
                fields='files(id, name)',
                pageToken=None
            ).execute()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Thành Công!',
                    'message': f'Kết nối Google Drive OK. Folder có {len(results.get("files", []))} file.',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(f'Không thể kết nối Google Drive: {str(e)}')

    def upload_file_to_drive(self, file_name, file_content, file_type='application/pdf'):
        """Upload file lên Google Drive"""
        if not self.bat_backup:
            return None

        try:
            service = self._get_drive_service()
            
            folder_id = self.thu_muc_cha_id.strip() if self.thu_muc_cha_id else ''
            # Tạo metadata file
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            # Convert file content
            if isinstance(file_content, str):
                file_content = file_content.encode()
            
            file_io = io.BytesIO(file_content)
            media = MediaIoBaseUpload(file_io, mimetype=file_type, resumable=True)

            # Upload
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            print(f'File uploaded: {file.get("name")} ({file.get("id")})')
            return {
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'link': file.get('webViewLink')
            }

        except Exception as e:
            print(f'Google Drive upload failed: {e}')
            raise Exception(f'Google Server Alert: {str(e)}')

    def create_folder_structure(self, folder_name):
        """Tạo thư mục con trên Google Drive"""
        try:
            service = self._get_drive_service()
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.thu_muc_cha_id]
            }

            folder = service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            return folder.get('id')
        except Exception as e:
            print(f'Create folder failed: {e}')
            return None
