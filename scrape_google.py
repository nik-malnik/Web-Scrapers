from apiclient.discovery import build

service = build("customsearch", "v1",
               developerKey="AIzaSyAw5qGVlFRr2lt29gyL5FxGW21dnrD7ZfM")

res = service.cse().list(
    q='faces',
    cx='012667766237131166296:yxgsotozehw',
    searchType='image',
    num=50,
    imgType='clipart',
    fileType='png',
    safe= 'off'
).execute()

if not 'items' in res:
    print 'No result !!\nres is: {}'.format(res)
else:
    for item in res['items']:
        print('{}:\n\t{}'.format(item['title'], item['link']))
