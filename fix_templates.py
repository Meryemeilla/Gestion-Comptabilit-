import os

files_to_fix = [
    r'c:\Users\lenovo\Downloads\Gestion-Comptabilité\templates\juridique\list.html',
    r'c:\Users\lenovo\Downloads\Gestion-Comptabilité\templates\fiscal\list.html',
    r'c:\Users\lenovo\Downloads\Gestion-Comptabilité\templates\dossiers\trash_list.html',
    r'c:\Users\lenovo\Downloads\Gestion-Comptabilité\templates\dossiers\list.html',
]

for file_path in files_to_fix:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # fix the '==' spacing in the templates
    fixed_content = content.replace("request.GET.type=='", "request.GET.type == '")
    
    if fixed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f'Fixed {file_path}')

# Fix comptables/list.html
comp_file = r'c:\Users\lenovo\Downloads\Gestion-Comptabilité\templates\comptables\list.html'
with open(comp_file, 'r', encoding='utf-8') as f:
    comp_content = f.read()

# fixing the split endif tag
fixed_comp_content = comp_content.replace("{%\n                            endif %}", "{% endif %}")
if fixed_comp_content != comp_content:
    with open(comp_file, 'w', encoding='utf-8') as f:
        f.write(fixed_comp_content)
    print(f'Fixed {comp_file}')
