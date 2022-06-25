f = input("Path >>> ")
with open(f, encoding='utf-8') as file:
    a = 1
    fw = open(f + '__0.txt', 'w')
    for line in file:
        if not line.startswith('Table:') or not line.startswith('Database:'):
            fw.write(line + '\n')
        else:
            fw = open(f + "__" + str(a) + '.txt', 'w')
            a += 1
