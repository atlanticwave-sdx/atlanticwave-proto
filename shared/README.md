# Shared Code

There are two types of shared code in the `shared` folder: interface objects and common libraries. We'll break them out below.

## Interface Objects

The interface objects are used between multiple different parts of the controller (_e.g._, the SDX controller and the local controllers). Interface objects that belong in a single part of the controller will live with that controller (_e.g._, the Ryu interface objects will live with the local controller code).

These are the bulk of the files that are in this directory. If they're not specifically called out in the "Common Libraries" section, they are an interface object.





## Common Libraries

The common libraries are used for a number of reasons, most often simplicity and seemless upgradability. In particular, we want to create an interface that can be used now, but the underlying technology can change. For example, the connection library right now is a plain TCP socket with some object packing using `pickle`. In the future, this could be TLS sockets using [protocol buffers](https://developers.google.com/protocol-buffers/).

### Connection Library

`Connection.py`
`ConnectionManager.py`

The connection library is used for inter-process communication both in between different parts of the controller (_e.g._, the SDX controller and local controllers) as well as between different modules in the same part (_e.g._, the Ryu interface and the rest of the local controller).


`SDXControllerConnectionManager.py`

This is an instance of `ConnectionManager` that is used to communicate between the SDX controller and the local controllers. It is being used to hold some constants that will likely be moved to a configuration file in the future.



### Singleton

`Singleton.py`

This is a very simiple class that's used for a standarized way of creating a singleton object. 