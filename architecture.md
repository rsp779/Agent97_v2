# Architecture

LangGraph Agent -> Tool Layer -> Repository Layer -> Data Access Layer -> JSON Storage

The DAL owns storage concerns only:
- lazy loading
- caching
- indexing
- joins and filtering

Repositories own business logic:
- customer risk views
- fraud investigation packages
- transaction summaries
- knowledge search

