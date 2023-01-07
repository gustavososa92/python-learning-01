db.createUser({
  user: "admin",
  pwd: "password",
  roles: [
    {
      role: "readWrite",
      db: "classify",
    },
  ],
});

newDb = db.getSiblingDB("classify");

newDb.users.insertOne(
  {
    "username":"admin",
    "isAdmin": true
  }
);