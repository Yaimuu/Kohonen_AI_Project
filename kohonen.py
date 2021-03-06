# coding: utf8
#!/usr/bin/env python
# ------------------------------------------------------------------------
# Carte de Kohonen
# Écrit par Mathieu Lefort
#
# Distribué sous licence BSD.
# ------------------------------------------------------------------------
# Implémentation de l'algorithme des cartes auto-organisatrices de Kohonen
# ------------------------------------------------------------------------
# Pour que les divisions soient toutes réelles (pas de division entière)
from __future__ import division
import math
from xmlrpc.client import MAXINT
# Librairie de calcul matriciel
import numpy
# Librairie d'affichage
import matplotlib.pyplot as plt



class Neuron:
  ''' Classe représentant un neurone '''
  
  def __init__(self, w, posx, posy):
    '''
    @summary: Création d'un neurone
    @param w: poids du neurone
    @type w: numpy array
    @param posx: position en x du neurone dans la carte
    @type posx: int
    @param posy: position en y du neurone dans la carte
    @type posy: int
    '''
    # Initialisation des poids
    self.weights = w.flatten()
    # Initialisation de la position
    self.posx = posx
    self.posy = posy
    # Initialisation de la sortie du neurone
    self.y = 0.
  
  def compute(self,x):
    '''
    @summary: Affecte à y la valeur de sortie du neurone (i.e. la distance entre son poids et l'entrée)
    @param x: entrée du neurone
    @type x: numpy array
    '''
    # TODO
    self.y = numpy.linalg.norm(self.weights - x)

  def learn(self,eta,sigma,posxbmu,posybmu,x):
    '''
    @summary: Modifie les poids selon la règle de Kohonen
    @param eta: taux d'apprentissage
    @type eta: float
    @param sigma: largeur du voisinage
    @type sigma: float
    @param posxbmu: position en x du neurone gagnant (i.e. celui dont le poids est le plus proche de l'entrée)
    @type posxbmu: int
    @param posybmu: position en y du neurone gagnant (i.e. celui dont le poids est le plus proche de l'entrée)
    @type posybmu: int
    @param x: entrée du neurone
    @type x: numpy array
    '''
    # TODO (attention à ne pas changer la partie à gauche du =)
    self.weights[:] = self.weights + eta * numpy.exp(
            -((self.posx - posxbmu) ** 2 + (self.posy - posybmu) ** 2) / (2 * sigma ** 2)
        ) * (x - self.weights)

  def distance(self, neuron):
    return math.dist([self.posx, self.posy], [neuron.posx, neuron.posy])

class SOM:
  ''' Classe implémentant une carte de Kohonen. '''

  def __init__(self, inputsize, gridsize):
    '''
    @summary: Création du réseau
    @param inputsize: taille de l'entrée
    @type inputsize: tuple
    @param gridsize: taille de la carte
    @type gridsize: tuple
    '''
    # Initialisation de la taille de l'entrée
    self.inputsize = inputsize
    # Initialisation de la taille de la carte
    self.gridsize = gridsize
    # Création de la carte
    # Carte de neurones
    self.map = []    
    # Carte des poids
    self.weightsmap = []
    # Carte des activités
    self.activitymap = []
    for posx in range(gridsize[0]):
      mline = []
      wmline = []
      amline = []
      for posy in range(gridsize[1]):
        neuron = Neuron(numpy.random.random(self.inputsize),posx,posy)
        mline.append(neuron)
        wmline.append(neuron.weights)
        amline.append(neuron.y)
      self.map.append(mline)
      self.weightsmap.append(wmline)
      self.activitymap.append(amline)
    self.activitymap = numpy.array(self.activitymap)

  def compute(self,x):
    '''
    @summary: calcule de l'activité des neurones de la carte
    @param x: entrée de la carte (identique pour chaque neurone)
    @type x: numpy array
    '''
    # On demande à chaque neurone de calculer son activité et on met à jour la carte d'activité de la carte
    for posx in range(self.gridsize[0]):
      for posy in range(self.gridsize[1]):
        self.map[posx][posy].compute(x)
        self.activitymap[posx][posy] = self.map[posx][posy].y

  def learn(self,eta,sigma,x):
    '''
    @summary: Modifie les poids de la carte selon la règle de Kohonen
    @param eta: taux d'apprentissage
    @type eta: float
    @param sigma: largeur du voisinage
    @type sigma: float
    @param x: entrée de la carte
    @type x: numpy array
    '''
    # Calcul du neurone vainqueur
    bmux,bmuy = numpy.unravel_index(numpy.argmin(self.activitymap),self.gridsize)
    # Mise à jour des poids de chaque neurone
    for posx in range(self.gridsize[0]):
      for posy in range(self.gridsize[1]):
        self.map[posx][posy].learn(eta,sigma,bmux,bmuy,x)

  
      

  def scatter_plot(self,interactive=False):
    '''
    @summary: Affichage du réseau dans l'espace d'entrée (utilisable dans le cas d'entrée à deux dimensions et d'une carte avec une topologie de grille carrée)
    @param interactive: Indique si l'affichage se fait en mode interactif
    @type interactive: boolean
    '''
    # Création de la figure
    if not interactive:
      plt.figure()
    # Récupération des poids
    w = numpy.array(self.weightsmap)
    # Affichage des poids
    plt.scatter(w[:,:,0].flatten(),w[:,:,1].flatten(),c='k')
    # Affichage de la grille
    for i in range(w.shape[0]):
      plt.plot(w[i,:,0],w[i,:,1],'k',linewidth=1.)
    for i in range(w.shape[1]):
      plt.plot(w[:,i,0],w[:,i,1],'k',linewidth=1.)
    # Modification des limites de l'affichage
    plt.xlim(-1,1)
    plt.ylim(-1,1)
    # Affichage du titre de la figure
    plt.suptitle('Poids dans l\'espace d\'entree')
    # Affichage de la figure
    if not interactive:
      plt.show()

  def scatter_plot_2(self,interactive=False, prediction=False):
    '''
    @summary: Affichage du réseau dans l'espace d'entrée en 2 fois 2d (utilisable dans le cas d'entrée à quatre dimensions et d'une carte avec une topologie de grille carrée)
    @param interactive: Indique si l'affichage se fait en mode interactif
    @type interactive: boolean
    '''
    # Création de la figure
    if not interactive:
      plt.figure()
    # Affichage des 2 premières dimensions dans le plan
    plt.subplot(1,2,1)
    # Affichage de la droite générée à partir de deux positions motrices
    if prediction:
      firstPos = numpy.array((-0.5, 0))
      secondPos = numpy.array((2, 2.5))
      xdata, ydata = network.buildFirstPolynome(firstPos, secondPos)
    # Récupération des poids
    w = numpy.array(self.weightsmap)
    # Affichage des poids
    plt.scatter(w[:,:,0].flatten(),w[:,:,1].flatten(),c='k')
    # Affichage de la grille
    for i in range(w.shape[0]):
      plt.plot(w[i,:,0],w[i,:,1],'k',linewidth=1.)
    for i in range(w.shape[1]):
      plt.plot(w[:,i,0],w[:,i,1],'k',linewidth=1.)
    # Affichage des 2 dernières dimensions dans le plan
    plt.subplot(1,2,2)

    # Affichage de la courbe prédisant la suite des positions spatiales
    if prediction:
      network.predictFollowingPositions(xdata, ydata)

    # Récupération des poids
    w = numpy.array(self.weightsmap)
    # Affichage des poids
    plt.scatter(w[:,:,2].flatten(),w[:,:,3].flatten(),c='k')
    # Affichage de la grille
    for i in range(w.shape[0]):
      plt.plot(w[i,:,2],w[i,:,3],'k',linewidth=1.)
    for i in range(w.shape[1]):
      plt.plot(w[:,i,2],w[:,i,3],'k',linewidth=1.)
    # Affichage du titre de la figure
    plt.suptitle('Poids dans l\'espace d\'entree')
    # Affichage de la figure
    if not interactive:
      plt.show()

  def plot(self):
    '''
    @summary: Affichage des poids du réseau (matrice des poids)
    '''
    # Récupération des poids
    w = numpy.array(self.weightsmap)
    # Création de la figure
    f,a = plt.subplots(w.shape[0],w.shape[1])    
    # Affichage des poids dans un sous graphique (suivant sa position de la SOM)
    for i in range(w.shape[0]):
      for j in range(w.shape[1]):
        plt.subplot(w.shape[0],w.shape[1],i*w.shape[1]+j+1)
        im = plt.imshow(w[i,j].reshape(self.inputsize),interpolation='nearest',vmin=numpy.min(w),vmax=numpy.max(w),cmap='binary')
        plt.xticks([])
        plt.yticks([])
    # Affichage de l'échelle
    f.subplots_adjust(right=0.8)
    cbar_ax = f.add_axes([0.85, 0.15, 0.05, 0.7])
    f.colorbar(im, cax=cbar_ax)
    # Affichage du titre de la figure
    plt.suptitle('Poids dans l\'espace de la carte')
    # Affichage de la figure
    plt.show()

  def MSE(self,X):
    '''
    @summary: Calcul de l'erreur de quantification vectorielle moyenne du réseau sur le jeu de données
    @param X: le jeu de données
    @type X: numpy array
    '''
    # On récupère le nombre d'exemples
    nsamples = X.shape[0]
    # Somme des erreurs quadratiques
    s = 0
    # Pour tous les exemples du jeu de test
    for x in X:
      # On calcule la distance à chaque poids de neurone
      self.compute(x.flatten())
      # On rajoute la distance minimale au carré à la somme
      s += numpy.min(self.activitymap)**2
    # On renvoie l'erreur de quantification vectorielle moyenne
    return s/nsamples

  def auto_organising_mesuring(self):
    '''
    @summary: Calcul de la variances des distances entre les poids des neurones
    '''
    neurones = []
    distances = []
    for i in range(self.gridsize[0]):
      for j in range(self.gridsize[1]):
        x = self.weightsmap[i][j][0]
        y = self.weightsmap[i][j][1]
        neurones.append([x,y])

    # savedNeurones est utilisé pour éviter de calculer deux fois la distance entre deux poids de neurones
    # (exemple : A,B et B,A)
    savedNeurones = []
    for n1 in neurones:
      for n2 in neurones:
        if n1 != n2 and n2 not in savedNeurones:
          distance = math.dist([n1[0], n1[1]], [n2[0], n2[1]])
          distances.append(distance)
      savedNeurones.append(n1)
    mean = numpy.var(distances)
    return mean

  def getClosestNeuron(self, pos, type = 0):
    '''
    @summary: Recherche du neurone le plus proche de la position passée en entrée
    @param pos: Coordonnées (x, y) du point choisi
    @type pos: numpy.array
    @param type: Indique le type de la position à retourner (spatiale = 0, motrice = 1)
    @type type: int
    '''

    # Coordonées x et y du neuronne cible
    target_neuron = []
    min = MAXINT

    # Tous les poids de la carte
    weights = numpy.array(self.weightsmap)
    # Par défaut, on considère que la position récherché est spatiale
    quad_pos = [2, 3]
    if type == 1:
      quad_pos = [0, 1]
    
    for i in range(weights.shape[0]):
      for j in range(weights.shape[1]):
        # Poids courant
        x = numpy.array((weights[i, j, quad_pos[0]], weights[i, j, quad_pos[1]]))
        # On cherche le neurone ayant le poids le plus proche de l'entrée
        distance = math.dist(pos, x)
        if min > distance:
          min = distance
          target_neuron = [i, j]
    # On retourne le poids le plus proche de l'entrée
    n = weights[target_neuron[0]][target_neuron[1]]

    return numpy.array([n[quad_pos[0]], n[quad_pos[1]]])

  def predictFollowingPositions(self, xdata, ydata):
    '''
    @summary: Prediction de la suite des positions spatiales prise par la main à partir d'un ensemble de positions motrices
    @param xdata: Ensemble des abscisses des positions motrices
    @type xdata: ndarray
    @param ydata: Ensemble des abscisses des positions motrices
    @type ydata: list
    '''
    newDataX = []
    newDataY = []

    for i in range (len(xdata)):
      pos = numpy.array((xdata[i], ydata[i]))
      closestNeuron = self.getClosestNeuron(pos, 0)
      newDataX.append(closestNeuron[0])
      newDataY.append(closestNeuron[1])

    # Affichage de la droite composée de l'ensemble des points générés
    plt.plot(newDataX, newDataY, 'g', lw=5)


  def buildFirstPolynome(self, firstPos, secondPos):
    '''
    @summary: Construction d'un ensemble de positions motrices à partir de deux points
    @param firstPos: Coordonnées (x, y) de la première position
    @type firstPos: numpy.array
    @param secondPos: Coordonnées (x, y) de la deuxième position
    @type secondPos: numpy.array
    '''
    x = [firstPos[0], secondPos[0]]
    y = [firstPos[1], secondPos[1]]

    # Création de l'équation de la droite
    coef = numpy.polyfit(x, y, 1)
    polynome = numpy.poly1d(coef)

    # Fabrication des points
    xdata = numpy.linspace(x[0], x[1], 7)
    ydata = polynome(xdata)

    # Affichage de la droite composée de l'ensemble des points générés
    plt.plot(xdata, ydata, 'g', lw=5)
    plt.plot(x[0], y[0], 'ro', lw=5)
    plt.plot(x[1], y[1], 'ro', lw=5)

    return xdata, ydata

# -----------------------------------------------------------------------------
if __name__ == '__main__':
  # Création d'un réseau avec une entrée (2,1) et une carte (10,10)
    #TODO mettre à jour la taille des données d'entrée pour les données robotiques
  network = SOM((4,1),(10,10))
  # PARAMÈTRES DU RÉSEAU
  # Taux d'apprentissage
  ETA = 0.05
  # Largeur du voisinage
  SIGMA = 1.4
  # Nombre de pas de temps d'apprentissage
  N = 10000
  # N = 1000
  # Affichage interactif de l'évolution du réseau 
    #TODO à mettre à faux pour que les simulations aillent plus vite
  VERBOSE = True
  # Nombre de pas de temps avant rafraissichement de l'affichage
  NAFFICHAGE = 1000
  # DONNÉES D'APPRENTISSAGE
  # Nombre de données à générer pour les ensembles 1, 2 et 3
    # TODO décommenter les données souhaitées
  nsamples = 1200
    # Ensemble de données 1
  # samples = numpy.random.random((nsamples,2,1))*2-1
  # print(samples)
    # Ensemble de données 2
  # samples1 = -numpy.random.random((nsamples//3,2,1))
  # samples2 = numpy.random.random((nsamples//3,2,1))
  # samples2[:,0,:] -= 1
  # samples3 = numpy.random.random((nsamples//3,2,1))
  # samples3[:,1,:] -= 1
  # samples = numpy.concatenate((samples1,samples2,samples3))
    # Ensemble de données 3
  # samples1 = numpy.random.random((nsamples//2,2,1))
  # samples1[:,0,:] -= 1
  # samples2 = numpy.random.random((nsamples//2,2,1))
  # samples2[:,1,:] -= 1
  # samples = numpy.concatenate((samples1,samples2))
    # Ensemble de données 4 (Sigmoïde)
  # i = 0
  # theta = numpy.zeros((nsamples,2,1))
  # for t in numpy.linspace(-numpy.pi,numpy.pi, nsamples):
  #   r = t**2
  #   theta[i,0,:] = r * numpy.cos(t) / (numpy.pi*2) + 0.75
  #   theta[i,1,:] = r * numpy.sin(t) / (numpy.pi*2)
  #   i += 1
  # samples = theta
    # Ensemble de données 5 (Spirale)
  # i = 0
  # theta = numpy.zeros((nsamples,2,1))
  # for t in numpy.linspace(-numpy.pi*10,numpy.pi*10, nsamples):
  #   r = t**2
  #   theta[i,0,:] = i * numpy.cos(t) / nsamples
  #   theta[i,1,:] = i * numpy.sin(t) / nsamples
  #   i += 1
  # samples = theta
    # Ensemble de données robotiques
  samples = numpy.random.random((nsamples,4,1))
  samples[:,0:2,:] *= numpy.pi
  l1 = 0.7
  l2 = 0.3
  samples[:,2,:] = l1*numpy.cos(samples[:,0,:])+l2*numpy.cos(samples[:,0,:]+samples[:,1,:])
  samples[:,3,:] = l1*numpy.sin(samples[:,0,:])+l2*numpy.sin(samples[:,0,:]+samples[:,1,:])
  # Affichage des données (pour les ensembles 1, 2 et 3)
  # plt.figure()
  # plt.scatter(samples[:,0,0], samples[:,1,0])
  # plt.xlim(-1,1)
  # plt.ylim(-1,1)
  # plt.suptitle('Donnees apprentissage')
  # plt.show()
    # Affichage des données (pour l'ensemble robotique)
  plt.figure()
  plt.subplot(1,2,1)
  plt.scatter(samples[:,0,0].flatten(),samples[:,1,0].flatten(),c='k')
  plt.subplot(1,2,2)
  plt.scatter(samples[:,2,0].flatten(),samples[:,3,0].flatten(),c='k')
  plt.suptitle('Donnees apprentissage')
  plt.show()
  # SIMULATION
  # Affichage des poids du réseau
  network.plot()
  # Initialisation de l'affichage interactif
  if VERBOSE:
    # Création d'une figure
    plt.figure()
    # Mode interactif
    plt.ion()
    # Affichage de la figure
    plt.show()
  # Boucle d'apprentissage
  for i in range(N+1):
    # Choix d'un exemple aléatoire pour l'entrée courante
    index = numpy.random.randint(nsamples)
    x = samples[index].flatten()
    # Calcul de l'activité du réseau
    network.compute(x)
    # Modification des poids du réseau
    network.learn(ETA,SIGMA,x)
    # Mise à jour de l'affichage
    if VERBOSE and i%NAFFICHAGE==0:
      # Effacement du contenu de la figure
      plt.clf()
      # Remplissage de la figure
        # TODO à remplacer par scatter_plot_2 pour les données robotiques
      # network.scatter_plot(True)
      network.scatter_plot_2(True)
      # Affichage du contenu de la figure
      plt.pause(0.00001)
      plt.draw()
  # Fin de l'affichage interactif
  if VERBOSE:
    # Désactivation du mode interactif
    plt.ioff()

  network.scatter_plot_2(True, True)
  plt.draw()

  # Affichage des poids du réseau
  network.plot()
  # Affichage de l'erreur de quantification vectorielle moyenne après apprentissage
  print("Erreur de quantification vectorielle moyenne ",network.MSE(samples))
  print("Mesure d'auto-organisation du réseau ",network.auto_organising_mesuring())

  pos_bras = numpy.array((1, 1))
  estimated_mot = network.getClosestNeuron(pos_bras, 1)

  print(f"Position du bras : (x1, x2), {pos_bras} - Position motrice estimée : (t1, t2), {estimated_mot}")

  pos_mot = numpy.array((0.75, 0.25))
  estimated_bras = network.getClosestNeuron(pos_mot, 0)

  print(f"Position motrice : (t1, t2), {pos_mot} - Position du bras estimée : (x1, x2), {estimated_bras}")