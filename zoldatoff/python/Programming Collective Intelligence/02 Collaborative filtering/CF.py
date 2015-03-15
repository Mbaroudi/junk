#!/usr/bin/env python
# coding: utf-8

"""
Вторая глава книги "Программируем коллективный разум"
Выработка рекомендаций
Collaborative filtering (CF)
"""

# A dictionary of movie critics and their ratings of a small
# set of movies
CRITICS = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5
    },
    'Toby': {
        'Snakes on a Plane': 4.5,
        'You, Me and Dupree': 1.0,
        'Superman Returns': 4.0
    }
}


from math import sqrt


def sim_distance(prefs, p1, p2):
    """
    Returns a distance-based similarity score for p1 and p1

    >>> sim_distance(CRITICS, 'Lisa Rose', 'Gene Seymour')
    0.14814814814814814
    """
    # Get the list of shared_items
    si = []
    for item in prefs[p1]:
        if item in prefs[p2]:
            si.append(item)

    # if they have no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Add up the squares of all the differences
    sum_of_squares = sum(
        [pow(prefs[p1][item] - prefs[p2][item], 2) for item in si]
    )

    return 1 / (1 + sum_of_squares)


def sim_pearson(prefs, p1, p2):
    """
    Returns the Pearson correlation coefficient for p1 and p2
    https://ru.wikipedia.org/wiki/Корреляция

    >>> sim_pearson(CRITICS, 'Lisa Rose', 'Gene Seymour')
    0.39605901719066977
    """

    # Get the list of mutually rated items
    si = []
    for item in prefs[p1]:
        if item in prefs[p2]:
            si.append(item)

    # if they are no ratings in common, return 0
    if len(si) == 0:
        return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it]*prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - sum1*sum2/n
    den = sqrt((sum1Sq - pow(sum1, 2)/n) * (sum2Sq - pow(sum2, 2)/n))
    if den == 0:
        return 0

    r = num/den

    return r


def sim_tanimoto(prefs, p1, p2):
    """
    Коэффициент Танимото
    http://habrahabr.ru/post/104901/

    >>> sim_tanimoto(CRITICS, 'Gene Seymour', 'Lisa Rose')
    0.3333333333333333
    """

    data = {}
    for person in prefs:
        data[person] = {}
        for item in prefs[person]:
            if prefs[person][item] < 3.0:
                data[person][item] = 0.0
            else:
                data[person][item] = 1.0

    a, b = len(prefs[p1]), len(prefs[p2])
    c = 0.0

    for item in prefs[p1]:
        if data[p1][item] == data[p2][item]:
            c += 1.0

    return c / (a + b - c)



#######################################################
# Коллаборатвная фильтрация по схожести пользователей #
#######################################################

def topMatches(prefs, person, n=5, similarity=sim_pearson):
    """
    Returns the best matches for person from the prefs dictionary.
    Number of results and similarity function are optional params.

    >>> topMatches(CRITICS, 'Toby', n=2)
    [('Lisa Rose', 0.9912407071619299), ('Mick LaSalle', 0.9244734516419049)]
    """

    scores = [(other, similarity(prefs, person, other))
              for other in prefs
              if other != person]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    """
    Gets recommendations for a person by using a weighted average
    of every other user's rankings

    >>> getRecommendations(CRITICS, 'Toby')
    [(3.3477895267131013, 'The Night Listener'), (2.8325499182641614, 'Lady in the Water'), (2.5309807037655645, 'Just My Luck')]

    >>> getRecommendations(CRITICS, 'Toby', similarity=sim_distance)
    [(3.5002478401415877, 'The Night Listener'), (2.7561242939959363, 'Lady in the Water'), (2.461988486074374, 'Just My Luck')]
    """
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person:
            continue

        sim = similarity(prefs, person, other)

        # ignore scores of zero or lower
        if sim <= 0:
            continue

        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item]*sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total/simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort(reverse=True)
    return rankings


def transformPrefs(prefs):
    """
    Транспонирует данные о рекомендациях (значение переменной CRITICS)

    >>> movies = transformPrefs(CRITICS)
    >>> topMatches(movies, 'Superman Returns')
    [('You, Me and Dupree', 0.6579516949597695), ('Lady in the Water', 0.4879500364742689), ('Snakes on a Plane', 0.11180339887498941), ('The Night Listener', -0.1798471947990544), ('Just My Luck', -0.42289003161103106)]
    >>> getRecommendations(movies, 'Just My Luck')
    [(4.0, 'Michael Phillips'), (3.0, 'Jack Matthews')]
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


##################################################
# Коллаборатвная фильтрация по схожести образцов #
##################################################

def calculateSimilarItems(prefs, n=10, similarity=sim_distance):
    """
    Create a dictionary of items showing which other items they
    are most similar to.

    >>> calculateSimilarItems(CRITICS, n=1)
    {'Lady in the Water': [('You, Me and Dupree', 0.4)], 'Snakes on a Plane': [('Lady in the Water', 0.2222222222222222)], 'Just My Luck': [('Lady in the Water', 0.2222222222222222)], 'Superman Returns': [('Snakes on a Plane', 0.16666666666666666)], 'You, Me and Dupree': [('Lady in the Water', 0.4)], 'The Night Listener': [('Lady in the Water', 0.2857142857142857)]}
    """

    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c, len(itemPrefs))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=similarity)
        result[item] = scores

    return result


def getRecommendedItems(prefs, itemMatch, user):
    """
    Строит оценку непросмотренных фильмов на основании данных
    о схожести образцов (calculateSimilarItems)

    >>> itemsim=calculateSimilarItems(CRITICS, n=10, similarity=sim_distance)
    >>> getRecommendedItems(CRITICS, itemsim, 'Toby')
    [(3.182634730538922, 'The Night Listener'), (2.5983318700614575, 'Just My Luck'), (2.4730878186968837, 'Lady in the Water')]
    """

    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (item2, similarity) in itemMatch[item]:
            # Ignore if this user has already rated this item
            if item2 in userRatings:
                continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity*rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    rankings = [(score/totalSim[item], item) for item, score in scores.items()]
    # Return the rankings from highest to lowest
    rankings.sort(reverse=True)

    return rankings


def loadMovieLens(path='./data'):
    """
    Берёт из папки data данные о рейтингах фильмов
    Данные "MovieLens 100k "взяты отсюда:
    http://grouplens.org/datasets/movielens/

    >>> prefs=loadMovieLens()
    >>> getRecommendations(prefs, '87')[0:3]
    [(5.0, 'They Made Me a Criminal (1939)'), (5.0, 'Star Kid (1997)'), (5.0, 'Santa with Muscles (1996)')]
    """

    # >>> itemsim=calculateSimilarItems(prefs, n=50)
    # 100 / 1664
    # 200 / 1664
    # 300 / 1664
    # 400 / 1664
    # 500 / 1664
    # 600 / 1664
    # 700 / 1664
    # 800 / 1664
    # 900 / 1664
    # 1000 / 1664
    # 1100 / 1664
    # 1200 / 1664
    # 1300 / 1664
    # 1400 / 1664
    # 1500 / 1664
    # 1600 / 1664
    # >>> getRecommendedItems(prefs, itemsim, '87')[0:3]
    # [(5.0, "What's Eating Gilbert Grape (1993)"), (5.0, 'Walk in the Sun, A (1945)'), (5.0, 'Vertigo (1958)')]

    # Get movie titles
    movies = {}
    for line in open(path+'/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    # Load data
    prefs = {}
    for line in open(path+'/u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]] = float(rating)

    return prefs


if __name__ == "__main__":
    import doctest
    doctest.testmod()
