import csv
import xlsxwriter
from pathlib import Path
from abc import ABC, abstractmethod

from ..models.exceptions import ValidationException 

class Writer(ABC):
    header = ['Address', 'Private Key', 'Mnemonic', 'Wallet Name']
    folder_name = 'user_data/output_data'
    
    @classmethod
    def create_folder(cls):
        relative_path = Path(cls.folder_name)        
        relative_path.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def write_data(self, data):
        pass

class CsvWriter(Writer):
    def __init__(self, filename: str):
        self.create_folder()
        self.full_path = Path(Writer.folder_name) / (filename + '.csv')
    
    def write_data(self, data):
        with open(self.full_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)            
            csv_writer.writerow(Writer.header)
            
            csv_writer.writerows(data)


class ExcelWriter(Writer):
    def __init__(self, filename: str):
        self.create_folder()
        self.full_path = Path(Writer.folder_name) / (filename + '.xlsx') 
    
    def write_data(self, data):        
        workbook = xlsxwriter.Workbook(self.full_path)
        worksheet = workbook.add_worksheet()
        
        bold_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        
        worksheet.write_row(0, 0, Writer.header, bold_format)
        
        for row, account_data in enumerate(data, start=1):
            worksheet.write_row(row, 0, account_data)
        
        workbook.close()
        

class WriterFactory:
    @staticmethod
    def create_writer(
        format_type: str = '', 
        filename: str = 'accounts'
    ) -> Writer:
        format_type = format_type.lower()
        
        format_type_docs = {
            'excel' : ExcelWriter,
            'csv'   : CsvWriter
        }
        
        if format_type not in format_type_docs.keys():
            raise ValidationException(f'Unsupported format: {format_type}')
        
        return format_type_docs[format_type](filename)