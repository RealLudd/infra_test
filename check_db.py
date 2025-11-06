import pandas as pd
df = pd.read_excel('data/paco_consolidated.xlsx')
print('Current DB columns:')
print(df.columns.tolist())
print(f'\nTotal rows: {len(df)}')
print(f'Has total_received_eur: {"total_received_eur" in df.columns}')
print(f'Has value_assigned_eur: {"value_assigned_eur" in df.columns}')

