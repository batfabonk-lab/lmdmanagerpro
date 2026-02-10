import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print('📊 STRUCTURE FINALE UE/EC (Semestre 1):')
print('=' * 60)

cursor.execute('''
SELECT ue.code_ue, ue.intitule_ue, ec.code_ec, ec.intitule_ue
FROM core_ue ue
LEFT JOIN core_ec ec ON ec.code_ue_id = ue.code_ue
WHERE ue.classe_id = 'L1INFO' AND ue.semestre = 1
ORDER BY ue.code_ue, ec.code_ec
''')

current_ue = None
for row in cursor.fetchall():
    ue_code, ue_intitule, ec_code, ec_intitule = row
    if ue_code != current_ue:
        print(f'\n📚 {ue_code} - {ue_intitule}')
        current_ue = ue_code
    if ec_code:
        print(f'   └─ {ec_code} - {ec_intitule}')
    else:
        print(f'   └─ (pas d\'EC)')

conn.close()
