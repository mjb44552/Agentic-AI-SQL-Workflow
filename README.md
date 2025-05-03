
# Agentic Ski Resort Recommendation System

## Project Aim

This project aims to create an application which utalises agentic AI
systems to recommend ski resorts to users. 

Users could use this system to help them decide which ski resort to visit. The Agentic 
system will gather, analyse and summaries the characteristics, features and highlights of
each ski resort and return the information to the user in an easy read style. 

This systems will provide in seconds a holistic description of each ski resort. Users won't 
need to visit a copious number of websites to understand what the ski resorts are like. 

## Layout / UI

Users will interact with the AI agents through a chat interfance. This will create 

1. An intuitive interface for users.
2. The opportunity for users to customise their querys so that the agentic system returns the information they most need.

Ideally, upon querying the systems user are given three good ski resort options (and reducing analysis peralysis). 

## AI Agents 
1. Web Searcher:
    - Goal: Retrieve information from the web when required for the user. 
    - Limitations: Will only find text, images and videos.

2. Data Analyst:
    - Goal: to summarise numerical data about ski resorts and present its findings to users.
    - Limitations: the data being analysed will be in a database in the application. New data won't
    come from the web.

3. Weather Girl:
    - Goal: call the relevent API's to get up to date or historical weahter statistics for the user.
    - Limitations: the API's it'll call will be limited ot the API's this application has keys for. 

4. Skier (Beginner, Intermediate, Expert):
    - Goal: to describe the mountain experience according to the ability its hypothetical ability.

## System Prioritise

1. Develop the Agentic AI framework so that agents work harmoniously together. 
2. Build limitations and goals into the agents to ensure output is consistent and useful.
3. Build a basic user interface. 
