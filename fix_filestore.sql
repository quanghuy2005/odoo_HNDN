-- Fix attachment references
DELETE FROM ir_attachment WHERE file_size < 0;
DELETE FROM ir_attachment WHERE res_model IS NULL OR res_model = '';
UPDATE ir_attachment SET file_size = 0 WHERE file_size IS NULL;
