# Initialize Config Server Replica Set:

sleep 25

docker exec -it config-svr-1 mongosh --port 27018 --eval '
rs.initiate({
    _id: "config-svr-replica-set",
    configsvr: true,
    members: [
        { _id: 0, host: "config-svr-1:27018" },
        { _id: 1, host: "config-svr-2:27018" },
        { _id: 2, host: "config-svr-3:27018" }
    ]
});
rs.status();
'

sleep 10

# Initialize Shard 1 Replica Set:

docker exec -it shard-1-node-a mongosh --port 27018 --eval '
rs.initiate({
    _id: "shard-1-replica-set",
    members: [
        { _id: 0, host: "shard-1-node-a:27018" },
        { _id: 1, host: "shard-1-node-b:27018" },
        { _id: 2, host: "shard-1-node-c:27018" }
    ]
});
rs.status();
'

sleep 10

# Initialize Shard 2 Replica Set:

docker exec -it shard-2-node-a mongosh --port 27018 --eval '
rs.initiate({
    _id: "shard-2-replica-set",
    members: [
        { _id: 0, host: "shard-2-node-a:27018" },
        { _id: 1, host: "shard-2-node-b:27018" },
        { _id: 2, host: "shard-2-node-c:27018" }
    ]
});
rs.status();
'

sleep 10

# Initialize Shard 3 Replica Set:

docker exec -it shard-3-node-a mongosh --port 27018 --eval '
rs.initiate({
    _id: "shard-3-replica-set",
    members: [
        { _id: 0, host: "shard-3-node-a:27018" },
        { _id: 1, host: "shard-3-node-b:27018" },
        { _id: 2, host: "shard-3-node-c:27018" }
    ]
});
rs.status();
'

sleep 10

# Initialize Routers and Add Shards:

docker exec -it router mongosh --port 27018 --eval '
sh.addShard("shard-1-replica-set/shard-1-node-a:27018");
sh.addShard("shard-2-replica-set/shard-2-node-a:27018");
sh.addShard("shard-3-replica-set/shard-3-node-a:27018");
sh.status();
'
