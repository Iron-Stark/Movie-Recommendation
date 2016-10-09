# A dictionary of movie critics and their ratings of a small set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
'The Night Listener': 4.5, 'Superman Returns': 4.0,
'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

#Returns a distance based similarity score between person1 and person2
def sim_distance(prefs,person1,person2):
  #Get the list of shared items
  si={}
  for item in prefs[person1]:
    if item in prefs[person2]:
      si[item]=1
  if len(si)==0:
    return 0
  sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])
  return 1/(1+sum_of_squares)
#Returns the pearson correlation coefficient for p1 and p2
def sim_pearson(prefs,person1,person2):
  si={}
  for item in prefs[person1]:
    if item in prefs[person2]:
      si[item]=1
  n=len(si)
  #If they have no ratings in common return 0
  if n==0:
    return 0
  #Add up the preferences
  sum1=sum([prefs[person1][it] for it in si])
  sum2=sum([prefs[person2][it] for it in si])
  #Sum up the squares
  sum1sq=sum([pow(prefs[person1][it],2) for it in si])
  sum2sq=sum([pow(prefs[person2][it],2) for it in si])
  #Sum up the products
  psum=sum([prefs[person1][it]*prefs[person2][it] for it in si])
  #Calculate pearson score
  num=psum-(sum1*sum2/n)
  den=sqrt((sum1sq-pow(sum1,2)/n) * (sum2sq-pow(sum2,2)/n))
  if den==0:
    return 0
  r=num/den
  return r 
# Returns the best matches for person from the prefs dictionary
# Number of results and similarity function are optional parameters
def topMatches(prefs,person,n=5,similarity=sim_pearson):
	scores=[(similarity(prefs,person,other),other) for other in prefs if other!=person]
	scores.sort()
	scores.reverse()
	return scores[0:n]
 # Get recommendations for a person by using weighted average of every other users rating
def getRecommendations(prefs,person,similarity=sim_pearson):
	totals={}
	simSums={}
	for other in prefs:
		#don't compare me to myself
		if other==person:
			continue
		sim=similarity(prefs,other,person)
		#ignore scores of 0 or lower
		if sim<=0:
			continue
		for item in prefs[other]:
			#only score the movies I haven't seen yet
			if item not in prefs[person] or prefs[person][item]==0:
				#Similarity*score
				totals.setdefault(item,0)
				totals[item]+=prefs[other][item]*sim
				#Sum of similarities
				simSums.setdefault(item,0)
				simSums[item]+=sim
	#Create the normalized list
	rankings=[(totals/simSums[item],item) for item,totals in totals.items()]
	rankings.sort()
	rankings.reverse()
	return rankings
def transformprefs(prefs):
	result={}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item,{})
			#Flip the item and person
			result[item][person]=prefs[person][item]
	return result

def CalculateSimilarItems(prefs,n=10):
	#Create a dictionary of items showing which other items they are most similar to
	result={}
	#Invert the preference metric to be item-centric
	itemPrefs=transformprefs(prefs)
	c=0
	for item in itemPrefs:
		#Status updates for large datasets
		c+=1
		if c%100==0:
			print "%d / %d" %(c,len(itemPrefs))
			#Find the most similar items to this one
			scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
			result[item]=scores
	return result
def getRecommendedItems(prefs,itemMatch,user):
 	userRatings=prefs[user]
 	scores={}
 	totalSim={}
 	#Loop over items rated by this user
 	for (item,rating) in userRatings.items():
 		#Loop over items similar to this one
 		for (similarity,item2) in itemMatch[item]:
 			#Ignore if this user has already rated the item
 			if item2 in userRatings:
 				continue
 			#Weighted sum of rating times similarity
 			scores.setdefault(item2,0)
 			scores[item2]+=similarity*rating
 			#Sum of all similarities
 			totalSim.setdefault(item2,0)
 			totalSim[item2]+=similarity
 	#Divide each total score by total weighting to get an average
 	rankings=[(score/totalSim[item],item) for item,score in scores.items()]
 	rankings.sort()
 	rankings.reverse()
 	return rankings
def loadMovieLens(path= '/home/ironstark/Desktop/Sign-ups-Predictor/ml-100k'):
	#Get movie titles
	movies={}
	for line in open(path+'/u.item'):
		(id,title)=line.split('|')[0:2]
		movies[id]=title
	#Load data
	prefs={}
	for line in open(path+'/u.data'):
		(user,movieid,rating,ts)=line.split('\t')
		prefs.setdefault(user,{})
		prefs[user][movies[movieid]]=float(rating)
	return prefs


