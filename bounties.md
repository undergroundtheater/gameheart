## Unclaimed Bounties

#Restful API
Our current database uses badly structured javascript and HTML with overly-complex forms to update data in what should be asynchronous calls.  To this end, we wish to create a REST API for the following models in GameHeart:

Character
CharacterTrait
Event
Attendance

In addition, we’d like a REST API for a virtual model, “CharacterSheet” - which will include all related objects to a Character.  User / Staff information should be used for any tokens or headers generated so that appropriate access can be determined.  4 tiers of access should exist: Anonymous, Patron, Staff, and Superuser (“isadmin”).  Anonymous will not have any access for this implementation, but should be considered.

The short-term goal is to use the REST API for creating a better, more responsive interface, without having to remove the old.  The long-term goal is to extend this REST API further to allow client applications using OAuth2 or similar mechanisms to access data as appropriate for games, registration or other tools.

The Chief of Technology for Underground Theater will be a point of contact for questions and answers about the current codebase, as the original developer is no longer available and did not provide documentation.  Fixtures for testing with real-world data can be provided upon request. 
