from users.deepseek_service import DeepSeekQuestionGenerator

gen = DeepSeekQuestionGenerator()
qb = gen.question_bank

print('=' * 60)
print('ASSESSMENT SYSTEM STATISTICS')
print('=' * 60)
print(f'\nTotal Industries Covered: {len(qb)}')
print(f'\nIndustries:')
for cat in sorted(qb.keys()):
    print(f'  - {cat.replace("_", " ").title()}')

total_q = sum(len(qb[cat].get(lvl, [])) for cat in qb for lvl in ['entry', 'intermediate', 'senior', 'expert'])
print(f'\nTotal Questions: {total_q}')
print(f'\nQuestions by Level:')
for lvl in ['entry', 'intermediate', 'senior', 'expert']:
    count = sum(len(qb[cat].get(lvl, [])) for cat in qb)
    print(f'  {lvl.title()}: {count}')

print(f'\nQuestions by Industry:')
for cat in sorted(qb.keys()):
    total = sum(len(qb[cat].get(lvl, [])) for lvl in ['entry', 'intermediate', 'senior', 'expert'])
    print(f'  {cat.replace("_", " ").title()}: {total}')
