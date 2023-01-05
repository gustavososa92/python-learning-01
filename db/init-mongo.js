db.createUser({
  user: "admin",
  pwd: "password",
  roles: [
    {
      role: "readWrite",
      db: "firstdb",
    },
    {
      role: "readWrite",
      db: "sentencesDatabase",
    },
    {
      role: "readWrite",
      db: "similarity",
    },
  ],
});

newDb = db.getSiblingDB("similarity");

newDb.users.insertOne(
  {
    "username":"admin",
    "password":"admin",
    "isAdmin": true
  }
);