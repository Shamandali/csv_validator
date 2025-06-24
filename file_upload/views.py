from django.shortcuts import render
from .forms import UploadFileForm

import csv
import io
import re



def upload_file(request):
    message = None
    errors = []
    validated_rows = []


    if request.method == 'POST':
        
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            try:
                data = uploaded_file.read().decode('utf-8')
                reader = csv.reader(io.StringIO(data), skipinitialspace=True)
                rows = list(reader)
                
                if not rows:
                    message = ""
                elif any(len(row) != 5 for row in rows):

                    invalid_rows = []
                    for i, row in enumerate(rows, start=1):
                        if len(row) != 5:
                            invalid_rows.append(f"Row {i}: {len(row)} columns")
                    
                    message = f"⚠️ El archivo debe contener exactamente 5 columnas."
                else:
                    # Validaciones específicas por cada columna
                    validated_rows = rows 
                    for i, row in enumerate(rows, start=1):
                       
                        if not row[0].isdigit() or not (3 <= len(row[0]) <= 10):
                            errors.append(f"fila {i}: Columna 1: Solo debe permitir números enteros entre 3 y 10 caracteres, se obtuvo '{row[0]}'")
                        
                        if not re.match(r"[^@]+@[^@]+\.[^@]+", row[1]):
                            errors.append(f"fila {i}: Columna 2: Solo debe permitir correos electrónicos, se obtuvo '{row[1]}'")
                        
                        if row[2] not in ['CC', 'TI']:
                            errors.append(f"fila {i}: Columna 3: Solo debe permitir los valores “CC” o “TI”, se obtuvo '{row[2]}'")
                        
                        if not row[3].isdigit():
                            errors.append(f"fila {i}: Columna 4 debe ser númerico, se obtuvo '{row[3]}'")
                        else:
                            value = int(row[3])
                            if not (500000 <= value <= 1500000):
                                errors.append(f"fila {i}: Columna 4: Solo debe permitir valores entre 500000 y 1500000, se obtuvo '{value}'")
                        
                    
                    if errors:
                        message = f"⚠️ El archivo es invalido ({len(errors)} errores encontrados)"
                        for error in errors:
                            print(f"  - {error}")
                    else:
                        valid_count = len(rows)
                        message = f"✅ El archivo es valido - {valid_count} filas procesadas correctamente"
                        
            except UnicodeDecodeError:
                message = "⚠️ Error procesando el archivo. Por favor asegurese que sea de tipo .txt"
            except Exception as e:
                message = f"⚠️ Error procesando el archivo: {str(e)}"
    else:
        form = UploadFileForm()

    return render(request, 'file_upload/upload.html', {
        'form': form,
        'message': message, 
        'errors': errors,
        'rows': validated_rows 
    })
