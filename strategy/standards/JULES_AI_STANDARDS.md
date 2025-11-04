# Jules AI Standards

**Status**: ✅ ACTIVE
**Last Updated**: 2025-11-04
**Owner**: Platform Team
**Applies To**: All Jules AI implementations across all Pact Platform services

---

## Purpose

This document defines the centralized standards and guidelines for Jules AI when implementing code across any Pact Platform service. All service-specific `AGENTS.md` files should reference this document.

---

## Jules AI Role Definition

**Jules AI** is the implementation specialist that:
- ✅ Implements code based on Claude's `planning.md` specifications
- ✅ Writes comprehensive tests (minimum 80% coverage)
- ✅ **Performs thorough self-review before marking work complete**
- ✅ Asks clarifying questions when requirements are ambiguous
- ✅ Follows all code quality and security standards

**CRITICAL**: Jules performs self-review. Claude does NOT review Jules' code. Human performs final approval only.

---

## Mandatory Self-Review Checklist

**Before marking ANY task complete, Jules MUST verify ALL items:**

### Security ✅
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] All user inputs validated and sanitized
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] Authentication/authorization properly implemented
- [ ] Sensitive data encrypted appropriately
- [ ] Error messages don't leak sensitive information
- [ ] HTTPS enforced for sensitive operations
- [ ] Rate limiting implemented where needed
- [ ] OWASP Top 10 vulnerabilities addressed

### Code Quality ✅
- [ ] Follows existing patterns in the codebase
- [ ] Functions are small and focused (< 50 lines preferred)
- [ ] Variable/function names are clear and descriptive
- [ ] No code duplication (DRY principle)
- [ ] No unused imports or dead code
- [ ] Comments explain WHY, not WHAT
- [ ] TypeScript types properly defined (if TypeScript)
- [ ] Python type hints used (if Python)
- [ ] Consistent code formatting with project standards

### Testing ✅
- [ ] All business logic has unit tests
- [ ] All API endpoints have integration tests
- [ ] Edge cases are tested
- [ ] Error paths are tested
- [ ] Test coverage ≥ 80%
- [ ] All tests pass
- [ ] No flaky tests
- [ ] Test names clearly describe what is tested

### Performance ✅
- [ ] No N+1 query problems
- [ ] Database queries optimized (indexes, pagination)
- [ ] Caching implemented where appropriate
- [ ] Async/await used for I/O operations
- [ ] Resources properly cleaned up (connections, timers)
- [ ] Large data sets handled with streaming/pagination
- [ ] No memory leaks

### Error Handling ✅
- [ ] All async operations have try/catch
- [ ] Errors are logged with context
- [ ] User-friendly error messages
- [ ] Proper HTTP status codes
- [ ] No sensitive info in error messages
- [ ] Retry logic for transient failures
- [ ] Circuit breakers for external services (if applicable)

### Completeness ✅
- [ ] All requirements from task description implemented
- [ ] All edge cases handled
- [ ] No TODOs or FIXMEs left in code
- [ ] Documentation updated (if needed)
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Ready for human review

---

## Code Standards by Language

### TypeScript/JavaScript

**Service Pattern:**
```typescript
export class MyService {
  constructor(
    private dependency1: Dependency1,
    private dependency2: Dependency2,
    private logger: Logger
  ) {}

  async myMethod(param: string): Promise<Result> {
    try {
      this.logger.info('Starting myMethod', { param });

      // Implementation
      const result = await this.dependency1.doSomething(param);

      this.logger.info('Completed myMethod', { result });
      return result;
    } catch (error) {
      this.logger.error('Error in myMethod', { error, param });
      throw new ServiceError('User-friendly message', error);
    }
  }
}
```

**Route Handler Pattern:**
```typescript
router.post('/endpoint', async (req, res) => {
  try {
    const result = await service.method(req.body);
    res.json({ success: true, data: result });
  } catch (error) {
    const statusCode = error.statusCode || 500;
    res.status(statusCode).json({
      success: false,
      error: error.message
    });
  }
});
```

**Test Pattern:**
```typescript
describe('MyService', () => {
  let service: MyService;
  let mockDep1: jest.Mocked<Dependency1>;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    mockDep1 = createMock<Dependency1>();
    mockLogger = createMock<Logger>();
    service = new MyService(mockDep1, mockLogger);
  });

  it('should handle happy path', async () => {
    mockDep1.doSomething.mockResolvedValue({ success: true });

    const result = await service.myMethod('input');

    expect(result).toBeDefined();
    expect(mockDep1.doSomething).toHaveBeenCalledWith('input');
  });

  it('should handle error case', async () => {
    mockDep1.doSomething.mockRejectedValue(new Error('Failed'));

    await expect(service.myMethod('bad')).rejects.toThrow();
    expect(mockLogger.error).toHaveBeenCalled();
  });
});
```

### Python

**Service Pattern:**
```python
from typing import Optional
import logging

class MyService:
    def __init__(
        self,
        dependency1: Dependency1,
        dependency2: Dependency2,
        logger: logging.Logger
    ):
        self.dependency1 = dependency1
        self.dependency2 = dependency2
        self.logger = logger

    async def my_method(self, param: str) -> Result:
        try:
            self.logger.info(f"Starting my_method with param={param}")

            # Implementation
            result = await self.dependency1.do_something(param)

            self.logger.info(f"Completed my_method: {result}")
            return result
        except Exception as error:
            self.logger.error(f"Error in my_method: {error}", exc_info=True)
            raise ServiceError("User-friendly message") from error
```

**Route Handler Pattern (FastAPI):**
```python
@router.post("/endpoint")
async def handle_endpoint(request: RequestModel) -> ResponseModel:
    try:
        result = await service.method(request)
        return ResponseModel(success=True, data=result)
    except ServiceError as error:
        raise HTTPException(
            status_code=error.status_code or 500,
            detail=str(error)
        )
```

**Test Pattern:**
```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestMyService:
    @pytest.fixture
    def service(self):
        mock_dep1 = Mock(spec=Dependency1)
        mock_logger = Mock(spec=logging.Logger)
        return MyService(mock_dep1, mock_logger)

    @pytest.mark.asyncio
    async def test_happy_path(self, service):
        service.dependency1.do_something = AsyncMock(return_value={"success": True})

        result = await service.my_method("input")

        assert result is not None
        service.dependency1.do_something.assert_called_once_with("input")

    @pytest.mark.asyncio
    async def test_error_case(self, service):
        service.dependency1.do_something = AsyncMock(side_effect=Exception("Failed"))

        with pytest.raises(ServiceError):
            await service.my_method("bad")
```

---

## Communication Protocol

### Status Updates

Provide clear updates at key milestones:
- "Plan generated and ready for approval"
- "Implementation started"
- "Tests written and passing (X% coverage)"
- "Self-review in progress (Y% complete)"
- "Self-review complete - ready for human review"

### Example Good Status Update

```
Status Update - Password Reset Implementation

✅ Completed:
- Token generation with crypto.randomBytes(32)
- Token hashing before storage (bcrypt)
- Email sending with reset link
- Rate limiting (3 requests/hour per IP)
- 15 tests written (89% coverage)

🔍 Self-Review:
- Security checklist: ✅ PASSED
- Code quality: ✅ PASSED
- Testing: ✅ PASSED (89% > 80% requirement)
- Performance: ✅ PASSED
- Edge cases: ✅ ALL HANDLED

🚀 Ready for human review
```

### When Requirements Are Unclear

If Jules encounters ambiguity:

1. **State the ambiguity clearly**
   - "The requirement says X, but existing code does Y"
   - "Security best practice recommends A, but planning.md says B"

2. **Propose 2-3 solutions with pros/cons**
   - Option 1: Follow requirement (pros/cons)
   - Option 2: Follow existing code (pros/cons)
   - Option 3: Hybrid approach (pros/cons)

3. **Recommend best option with technical reasoning**
   - "I recommend Option 2 because [security/performance/maintainability]"

4. **Wait for confirmation**
   - Do NOT proceed until clarification received

### Example Good Question

```
Ambiguity Found:

Issue: planning.md specifies token expiry as "1 hour" but
OWASP best practices recommend "15 minutes" for password
reset tokens.

Options:
1. Use 1 hour (as specified in planning.md)
   Pros: Matches specification, more user-friendly
   Cons: Larger attack window, security risk

2. Use 15 minutes (OWASP recommendation)
   Pros: Reduces attack window, industry standard
   Cons: May require users to request reset again

3. Make configurable via environment variable
   Pros: Flexible, can adjust per environment
   Cons: Added complexity, configuration drift risk

Recommendation: Option 2 (15 minutes)
Reasoning: Security should be prioritized over convenience
for password reset operations. 15 minutes is sufficient
for legitimate users while minimizing attack window.
OWASP recommendations exist for good reason.

Waiting for confirmation before proceeding.
```

---

## Edge Cases to Handle

### Authentication/Authorization
- User not found → Generic message (don't reveal if user exists)
- Invalid token → Clear error message
- Token expired → Clear error message
- Insufficient permissions → 403 status
- Session expired → 401 status with re-auth required

### Validation
- Missing required fields → 400 with specific field list
- Invalid format → 400 with validation errors
- Data too large → 413 status
- Invalid enum value → 400 with allowed values

### External Services
- Service down → Queue for retry or return fallback response
- Timeout → Retry with exponential backoff (3 attempts max)
- Rate limited → Respect retry-after header
- Circuit breaker open → Fallback behavior

### Database
- Record not found → 404 status
- Duplicate key → 409 status with conflict details
- Concurrent update → Optimistic locking or 409 status
- Connection lost → Retry with backoff
- Deadlock → Retry transaction (3 attempts max)

### File Operations
- File not found → 404 status
- Permission denied → 403 status
- Disk full → 507 status
- File too large → 413 status

---

## Completion Criteria

**Only mark work complete when ALL of these are true:**

1. ✅ All requirements from task description implemented
2. ✅ All tests passing (≥80% coverage)
3. ✅ Self-review checklist 100% complete
4. ✅ No security vulnerabilities
5. ✅ No TODOs or FIXMEs in production code
6. ✅ All edge cases handled
7. ✅ Documentation updated
8. ✅ Code follows existing patterns
9. ✅ No breaking changes (or documented if necessary)
10. ✅ Performance is acceptable (no obvious bottlenecks)

**If any item is incomplete, keep working. Do NOT mark complete early.**

---

## Task Interpretation Guidelines

When Jules receives a task from Claude, it will include:

1. **Feature/Bug Description** - What needs to be done
2. **Context** - Why it's needed
3. **Requirements** - Specific specifications
4. **Reference Documents** - `planning.md`, existing code patterns
5. **Jules Guidelines** - Rules to follow (this document)
6. **Expected Deliverables** - Files to create/modify

**Jules MUST:**
- Read `planning.md` completely
- Study referenced files to understand existing patterns
- Follow all requirements exactly as specified
- Complete self-review checklist 100%
- Provide clear status updates
- Ask questions when unclear (don't assume)

---

## Security Standards (Expanded)

### Input Validation
- Validate all user inputs at API boundary
- Use allow-lists rather than deny-lists
- Sanitize inputs before using in queries/commands
- Validate data types, lengths, formats
- Check for null/undefined values

### Authentication & Authorization
- Never trust client-provided user IDs
- Verify authentication tokens on every request
- Check authorization for every protected resource
- Use secure session management
- Implement proper logout functionality

### Data Protection
- Encrypt sensitive data at rest
- Use TLS/HTTPS for data in transit
- Never log sensitive data (passwords, tokens, PII)
- Implement proper key management
- Use secure random generators (crypto.randomBytes, secrets module)

### API Security
- Implement rate limiting
- Use CORS appropriately
- Validate Content-Type headers
- Implement CSRF protection where needed
- Set proper security headers

---

## Performance Standards

### Database
- Use indexes on frequently queried columns
- Implement pagination for large result sets
- Avoid N+1 queries (use joins or batch loading)
- Use database-level constraints
- Consider read replicas for read-heavy operations

### Caching
- Cache expensive computations
- Cache frequently accessed data
- Use appropriate TTLs
- Implement cache invalidation strategy
- Consider distributed caching for multi-instance deployments

### Asynchronous Operations
- Use async/await for I/O operations
- Don't block the event loop
- Use worker threads/processes for CPU-intensive tasks
- Implement proper error handling in async code
- Use connection pooling

---

## Cross-Service Standards

### API Design
- Follow RESTful conventions
- Use proper HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Return appropriate status codes
- Include pagination in list endpoints
- Version APIs appropriately

### Error Responses
- Consistent error format across all services
- Include error codes for programmatic handling
- Provide helpful error messages for developers
- Never expose internal implementation details
- Include correlation IDs for tracing

### Logging
- Log at appropriate levels (DEBUG, INFO, WARN, ERROR)
- Include context (user ID, request ID, correlation ID)
- Don't log sensitive data
- Use structured logging (JSON format)
- Include timestamps and service name

---

## Continuous Improvement

Jules should:
- Learn from existing codebase patterns
- Suggest improvements when appropriate
- Document non-obvious decisions
- Consider maintainability and future extensibility
- Balance perfection with pragmatism

**However**: When in doubt, follow existing patterns. Consistency is more valuable than individual perfection.

---

## Final Checklist Before Marking Complete

```
JULES SELF-REVIEW FINAL CHECKLIST

Security:
[ ] All inputs validated
[ ] No hardcoded secrets
[ ] Authentication/authorization correct
[ ] Error messages safe
[ ] OWASP Top 10 addressed

Code Quality:
[ ] Follows existing patterns
[ ] No duplication
[ ] Clear naming
[ ] Proper comments
[ ] No unused code

Testing:
[ ] ≥80% coverage
[ ] All tests pass
[ ] Edge cases tested
[ ] Error paths tested

Performance:
[ ] No N+1 queries
[ ] Proper async usage
[ ] Caching where appropriate
[ ] Resources cleaned up

Error Handling:
[ ] All paths have error handling
[ ] Proper logging
[ ] User-friendly messages
[ ] Correct status codes

Completeness:
[ ] All requirements met
[ ] All edge cases handled
[ ] No TODOs/FIXMEs
[ ] Documentation updated
[ ] Ready for human review

Self-Review Score: ___/6 sections
Only mark complete if ALL sections checked ✅
```

---

**Status**: ✅ ACTIVE
**Enforcement**: MANDATORY for all Jules AI implementations
**Next Review**: 2025-12-04
**Version**: 1.0

