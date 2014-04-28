# GameHeart

## Overview

Gameheart is an RPG management system built with [Underground Theater](http://www.undergroundtheater.org) in mind.  The data we use is proprietary, but the software is not.  In the interest of improving our experience and yours, we're opening up the source code under the MIT License.

### Underground Theater

Underground Theater (UT) is a Live-action roleplaying and social club, focused on White Wolf / CCP Games' classic World of Darkness using the modern rules.  If you are a patron or a user of their services, do not submit issues here for problems, instead use [their support site](http://support.undergroundtheater.org).

## Policies

At the moment, we are accepting volunteers to work directly on the code, including non-patrons.  We're screening for collaborator access at technology@undergroundtheater.org.  If you just want to talk shop about the project, you can request to join the "Tech Discussion" group over on our [Google Groups page](http://groups.undergroundtheater.org). Otherwise, we will accept pull requests for discussion of any nature on this repository - including proposed updates to this file.

### Issues / Bugs

Bugs specific to the engine or problems found during installation can be submitted here.  Bugs should not be specific to game data, but problems managing it - including structure problems.

## Current goals

Each goal is broken down later, but here's the high-level:

0. Generic
1. Improved Usability 
2. Improved Documentation 
3. Improved Deployment
3. Mobile
4. API / REST
5. Device-specific applications

### Generic

GameHeart may be the mechanical beating heart of Underground Theater, but it can be more.  A plugin system would likely make this possible; moving the UT-specific code into hooks would improve usability for other organizations and clubs and making our own proprietary improvements to our system possible.  This is marked at "1" because it should be kept in mind for all of the below, not necessarily implemented today. It's a priorty for certain.

### Improved Usability

Basically:

* Improved visibility for buttons
* Make views and templates context-sensitive as opposed to segmented, multiple views for the same data
* Pulling the data in one place isn't bad if you're caching some of the data or using a backend process to return a few pages of rows at a time
* Better error messages!!

### Improved Documentation

We're in a pretty poor state:

* Basic instance installation documentation is missing
* Storyteller and admin documentation
* Generic player documentation (sans [Underground Theater](http://www.undergroundtheater.org) chronicle information)

### Improved Deployment

Probably Puppet 3.  I would like it if anyone wanting to develop on this application can simply push a button to get a basic instance to play with.  It also would help make our production deployment(s) all the easier.

### Mobile

Using bootstrap 3 should solve most of this, but it can be improved with careful application of responsive design to our templates.

### API / REST

This is a given and a requirement for the next step anyway.  In addition, we can then open up patron-driven apps that use our data in an approved facebook-apps-esque manner.  Boon management apps? Want your own secure communications with your coterie? The possibilities are near endless.

### Device Apps

One day, we'd like to have an official app both of the popular platforms. Making a generic version of this application would mean others who contribute for their own uses have a new avenue to explore and manage their game data.
