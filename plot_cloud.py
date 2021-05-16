import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

with open('S204_answers.csv', 'r') as file:
    text = file.read().replace('\n', '')

fig = plt.figure(figsize=(40,30))
plt.axis("off")
wc = WordCloud(width=3000, height= 2000, random_state=1, background_color='black', colormap='Pastel1', collocations=False, stopwords=STOPWORDS).generate(text)
plt.imshow(wc)
fig.savefig('world_cloud.png', bbox_inches='tight')
