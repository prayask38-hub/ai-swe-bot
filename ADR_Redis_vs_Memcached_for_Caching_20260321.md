# ADR: Redis vs Memcached for Caching

**Date:** 2026-03-21  
**Status:** Accepted  
**Decision:** Redis  

---

## Context
Should we use Redis or Memcached for caching?

## Decision
Given the requirements for pub/sub and complex data structures, Redis is the better choice despite its higher resource requirements and steeper learning curve. Its support for persistent data storage and variety of data structures makes it a more versatile and reliable option for caching in a Python backend.

## Options Considered

### Redis (Score: 90/100)
**Best for:** Applications requiring pub/sub, complex data structures, and data persistence

**Pros:**
- Supports pub/sub messaging
- Supports complex data structures like lists, sets, and hashes
- Persistent data storage

**Cons:**
- Steeper learning curve
- More resource-intensive

**Used by:** Pinterest, Instagram, Twitter

### Memcached (Score: 60/100)
**Best for:** Simple caching use cases with high performance requirements

**Pros:**
- High performance
- Simple to implement
- Low resource requirements

**Cons:**
- Limited to simple key-value caching
- No pub/sub support
- No data persistence

**Used by:** Facebook, YouTube, Reddit

## Consequences
**Tradeoffs accepted:**
- Higher resource requirements
- Steeper learning curve

**Risks:**
- Increased resource usage
- Additional complexity in the system

## Implementation Steps
1. Install and configure Redis
2. Integrate Redis with Python backend using a library like redis-py
3. Implement pub/sub messaging and complex data structures

## When to Revisit
If caching requirements simplify or performance becomes a major concern
