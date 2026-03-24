# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class VanBanFullTextSearch(models.Model):
    """Model full-text search index cho văn bản"""
    _name = 'vanban.fulltext.search'
    _description = 'Full-Text Search Index - Văn bản'

    # Thông tin document
    vanban_model = fields.Char(
        string='Model văn bản',
        required=True,
        readonly=True,
        index=True
    )

    vanban_id = fields.Integer(
        string='ID văn bản',
        required=True,
        readonly=True,
        index=True
    )

    vanban_name = fields.Char(
        string='Tên/Số văn bản',
        readonly=True,
        index=True
    )

    # Nội dung index
    noi_dung_tich_hop = fields.Text(
        string='Nội dung tích hợp',
        help='Toàn bộ nội dung để search',
        readonly=True
    )

    # Thông tin xây dựng
    ngay_tao_index = fields.Datetime(
        string='Ngày tạo index',
        readonly=True,
        default=fields.Datetime.now
    )

    ngay_cap_nhat_index = fields.Datetime(
        string='Ngày cập nhật index',
        readonly=True
    )

    # Statistics
    so_lan_tim_thay = fields.Integer(
        string='Số lần tìm thấy',
        default=0,
        readonly=True
    )

    _sql_constraints = [
        ('unique_document', 'unique(vanban_model, vanban_id)', 
         'Chỉ có thể có 1 index cho mỗi văn bản!')
    ]

    @api.model
    def create_or_update_index(self, vanban_model, vanban_id):
        """
        Tạo hoặc cập nhật index cho văn bản
        """
        try:
            vanban = self.env[vanban_model].browse(vanban_id)
            vanban_name = vanban.name if hasattr(vanban, 'name') else f'{vanban_model}#{vanban_id}'

            # Tập hợp nội dung cần index
            noi_dung = self._build_indexable_content(vanban, vanban_model)

            # Check xem có index chưa
            existing = self.search([
                ('vanban_model', '=', vanban_model),
                ('vanban_id', '=', vanban_id)
            ])

            if existing:
                existing.write({
                    'noi_dung_tich_hop': noi_dung,
                    'ngay_cap_nhat_index': fields.Datetime.now()
                })
                return existing
            else:
                return self.create({
                    'vanban_model': vanban_model,
                    'vanban_id': vanban_id,
                    'vanban_name': vanban_name,
                    'noi_dung_tich_hop': noi_dung,
                })

        except Exception as e:
            _logger.error(f'Lỗi tạo/update index: {str(e)}')
            return False

    @api.model
    def _build_indexable_content(self, vanban, vanban_model):
        """
        Xây dựng nội dung để index từ văn bản
        """
        content_parts = []

        # Tên/Số văn bản
        if hasattr(vanban, 'name'):
            content_parts.append(str(vanban.name))

        # Trích yếu/tóm tắt
        if hasattr(vanban, 'trich_yeu'):
            content_parts.append(str(vanban.trich_yeu or ''))

        # Mô tả
        if hasattr(vanban, 'mo_ta'):
            content_parts.append(str(vanban.mo_ta or ''))

        # Content từ PDF (nếu có analyzer)
        if hasattr(vanban, 'analyzer_id') and vanban.analyzer_id:
            if hasattr(vanban.analyzer_id, 'noi_dung_trich_xuat'):
                content_parts.append(vanban.analyzer_id.noi_dung_trich_xuat)

            if hasattr(vanban.analyzer_id, 'tom_tat_ai'):
                content_parts.append(vanban.analyzer_id.tom_tat_ai)

        # Từ khóa
        if hasattr(vanban, 'tu_khoa'):
            content_parts.append(str(vanban.tu_khoa or ''))

        # Loại văn bản
        if hasattr(vanban, 'loai_van_ban'):
            content_parts.append(str(vanban.loai_van_ban or ''))

        # Cơ quan ban hành/nhận
        if hasattr(vanban, 'co_quan_ban_hanh'):
            content_parts.append(str(vanban.co_quan_ban_hanh or ''))
        if hasattr(vanban, 'co_quan_nhan'):
            content_parts.append(str(vanban.co_quan_nhan or ''))

        # Người ký
        if hasattr(vanban, 'nguoi_ky'):
            content_parts.append(str(vanban.nguoi_ky or ''))

        # Comment fields
        if hasattr(vanban, 'ghi_chu'):
            content_parts.append(str(vanban.ghi_chu or ''))

        # Về ghi chú duyệt (nếu có)
        if hasattr(vanban, 'nhan_xet_duyet'):
            content_parts.append(str(vanban.nhan_xet_duyet or ''))

        return '\n '.join([p for p in content_parts if p])

    @api.model
    def search_vanban(self, keyword, vanban_model=None):
        """
        Tìm kiếm văn bản theo từ khóa
        Trả về list (model, id, name, highlighted_snippet)
        """
        results = []

        try:
            # Xây dựng query
            domain = [('noi_dung_tich_hop', 'ilike', keyword)]
            if vanban_model:
                domain.append(('vanban_model', '=', vanban_model))

            # Tìm kiếm
            indexes = self.search(domain)

            for index in indexes:
                # Tăng counter
                index.so_lan_tim_thay += 1

                # Tạo highlight snippet
                snippet = self._create_highlight_snippet(
                    index.noi_dung_tich_hop,
                    keyword,
                    context_length=100
                )

                results.append({
                    'model': index.vanban_model,
                    'id': index.vanban_id,
                    'name': index.vanban_name,
                    'type': 'van_ban_den' if 'den' in index.vanban_model else 'van_ban_di',
                    'snippet': snippet,
                    'created': index.ngay_tao_index,
                })

            return results

        except Exception as e:
            _logger.error(f'Lỗi search: {str(e)}')
            return []

    @api.model
    def _create_highlight_snippet(self, text, keyword, context_length=100):
        """
        Tạo snippet highlight từ khóa
        """
        try:
            import re

            # Find position
            pattern = re.compile(keyword, re.IGNORECASE)
            match = pattern.search(text)

            if not match:
                return text[:context_length * 2] + '...'

            start = max(0, match.start() - context_length)
            end = min(len(text), match.end() + context_length)

            snippet = text[start:end]

            # Add ellipsis
            if start > 0:
                snippet = '...' + snippet
            if end < len(text):
                snippet = snippet + '...'

            # Highlight keyword
            highlighted = re.sub(
                f'({keyword})',
                r'<b>\1</b>',
                snippet,
                flags=re.IGNORECASE
            )

            return highlighted

        except:
            return text[:context_length * 2] + '...'

    def delete_index(self):
        """Delete index"""
        self.unlink()

    @api.model
    def rebuild_all_indexes(self):
        """Rebuild toàn bộ indexes (dùng cho migration)"""
        # TODO: Implement rebuild
        pass
