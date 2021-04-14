# \(Offline\) Registration Module App

Since the partner users who are registering in the field will have unreliable internet connectivity they will need the application running on their phone run offline.

### App options

Few options are considered for it:

* \#1 A completely native Android application.
* \#2 A React native application that works on both Android / iOS
* \#3 A Progressive Web App \(PWA\)

Option \#1 and \#3 are the ones to consider. Specifically option \#3 is compelling since it leverages the web technologies we will already be using.

### Offline storage / sync

We strongly suggest leveraging [https://github.com/redux-offline/redux-offline](https://github.com/redux-offline/redux-offline) - for our needs \(1-way sync\) it allows us to store data offline \(default uses [IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)\). When online this data would be synced \(1-way\) to the backend via API's. It can also use WebSQL/localStorage fallbacks via [localForage](https://github.com/localForage/localForage).

[PouchDB](https://pouchdb.com) can be considered as well, but it might overly complicated for our needs and shines more for 2-way sync of data and also when backend is CouchDB \(not in our architecture\).

### Enabling offline de-duplication

Enabling the scenario where the same person may register their household multiple times during enrollment when all devices are offline is tricky and will require a local server based solution. This may not fit into our architecture.

#### 

