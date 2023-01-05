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
})

use similarity

db.users.insertOne(
  {
    "username":"admin",
    "password":"admin",
    "isAdmin": true
  }
)