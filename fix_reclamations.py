import os

file_path = r'c:\Users\lenovo\Downloads\Gestion-Comptabilité\templates\reclamations\list.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# fix the '==' spacing
fixed_content = content.replace("selected_classement=='", "selected_classement == '")

# fix the split if tag
fixed_content = fixed_content.replace("{% if reclamation.created_by == user and reclamation.created_by.role !=\n                                    'administrateur' %}", "{% if reclamation.created_by == user and reclamation.created_by.role != 'administrateur' %}")

if fixed_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print('Fixed list.html')
else:
    print('No changes needed or match failed')
