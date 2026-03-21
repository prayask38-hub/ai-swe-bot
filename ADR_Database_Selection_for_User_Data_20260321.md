# ADR: Database Selection for User Data

**Date:** 2026-03-21  
**Status:** Accepted  
**Decision:** PostgreSQL  

---

## Context
Should we use PostgreSQL or MongoDB for our user data?

## Decision
Given the SaaS app's requirements for complex queries and the team's familiarity with SQL, PostgreSQL is the best choice due to its support for complex transactions, ACID compliance, and ability to handle the app's current scale of 100k users. While MongoDB offers flexibility and scalability, the app's needs for complex queries and the team's SQL proficiency make PostgreSQL a more suitable choice.

## Options Considered

### PostgreSQL (Score: 80/100)
**Best for:** Applications requiring strong consistency, complex transactions, and adherence to SQL standards

**Pros:**
- Maturity and stability
- Support for complex queries
- ACID compliance
- SQL support

**Cons:**
- Steep learning curve for advanced features
- May require additional support for horizontal scaling

**Used by:** Instagram, Pinterest, Reddit

### MongoDB (Score: 70/100)
**Best for:** Big data and real-time web applications with flexible schema requirements

**Pros:**
- Flexible schema
- High scalability and performance
- Easy data retrieval and manipulation

**Cons:**
- Lack of support for complex transactions
- Data consistency issues in distributed environments

**Used by:** LinkedIn, Foursquare, Shopify

## Consequences
**Tradeoffs accepted:**
- Potential need for additional support for horizontal scaling
- Steep learning curve for advanced PostgreSQL features

**Risks:**
- Data consistency issues during migration
- Performance bottlenecks if indexing is not properly optimized

## Implementation Steps
1. Set up PostgreSQL database cluster
2. Design database schema for user data
3. Implement data migration and backup strategies

## When to Revisit
Significant changes in user base size, query complexity, or the need for real-time data processing would necessitate re-evaluation of the database choice
