# Test Infrastructure Design

## 1. Configuration Management

Remove `DATABASE_URL` from `tox.ini`. Pass it from environment variable via `pass_env = DATABASE_URL`. pytest-django handles the rest automatically. Create `.env.test.example` as documentation for developers.

## 2. Startup Performance

**Status:** Requires investigation

Areas to examine:
- What exactly takes time (pytest startup profiling)
- Which fixtures are the biggest bottleneck
- Whether Elasticsearch wait is a problem
- Whether migrations/permissions can be optimized

## 3. Factory Design

Factories must be deterministic and simple.

**Rules:**

1. **Only static default values** - no Faker, FuzzyChoice, random. Factory creates a "minimal" object, test sets values relevant to the scenario.

2. **Sequence only for UNIQUE fields** - e.g., `unicef_id` must be unique, so Sequence is OK.

3. **Relations have no default values** - test explicitly passes related objects. Setup is visible in the test.

4. **Remove helper functions with business logic** - functions like `create_household` hide what's happening. Test builds its own setup.

**Migration:** New factories follow these rules, gradually refactor existing ones.

## 4. Fixture Strategy

Fixtures must be explicit and intentional.

**Rules:**

1. **Autouse ONLY for infrastructure** - cache clearing, logging disable, transaction rollback. Things that truly must run for every test.

2. **NO autouse for business data** - Partner, BusinessArea, Program - test must explicitly request these fixtures. Dependencies are visible.

3. **Fixtures per test/module, not global** - avoid magic fixtures from global conftest that are "just available".

4. **Scope intentionally** - `function` by default for isolation, `session` only for truly expensive operations (Elasticsearch setup).

## 5. Coverage Strategy

**Goal:** 100% line coverage with sensible exclusions.

**Tools:**
- `pytest --cov --cov-report=term-missing`
- CI fail if coverage drops

**Exclusions:**
- Migrations
- `__str__`, `__repr__`
- Management commands
- Dead code (remove instead of testing)

**Approach:**
- New code: 100% coverage required
- Existing code: establish baseline, gradually increase

## 6. Test Writing Guidelines

**Rules:**

1. **Test is documentation** - reading the test shows what we're testing and why. Setup, action, assertion in one place.

2. **Don't fear duplication** - better to repeat setup than hide in helpers.

3. **One test = one scenario** - don't test 5 things in one test.

4. **Names describe behavior** - `test_household_without_head_raises_error` instead of `test_household_validation`.

5. **Arrange-Act-Assert** - clearly separated sections.

6. **Mock only external dependencies** - API, email, time. Database and own models - real objects.

7. **Tests without conditionals** - no `if`, `else`, `for`. Test must be linear. If you need a condition, those are two scenarios and should be two tests.

## 7. Flaky Tests

**Problem:** `--reruns 3` in tox.ini masks flaky tests instead of fixing them.

**Rule:** If a test needs to be retried to pass, it's broken and needs to be fixed.

**Action:** Remove `--reruns` from configuration. Flaky test = bug to fix, not to hide.

## 8. Unit vs Integration Test Separation

**Problem:** Everything in `tests/unit/` but some tests use DB, Elasticsearch, external services.

**Division:**
- **Unit tests** - no DB, no external services, fast, test individual functions/classes in isolation
- **Integration tests** - with DB, may use external services, test component collaboration

**Structure:**
```
tests/
├── unit/           # no DB, fast
├── integration/    # with DB, slower
└── e2e/            # selenium, slowest
```

**Benefit:** Can run only unit tests for fast feedback during development.

## 9. Single Test Style

**Problem:** Mix of `TestCase` classes and pytest functions in codebase.

**Rule:** All new tests as pytest functions. Gradual migration of existing TestCase to pytest.

**Why pytest functions:**
- Simpler, less boilerplate
- Better fixtures (dependency injection)
- Better parametrize
- More readable

## 10. Test Speed Monitoring

**Rule:** Regularly monitor which tests are slow.

**Tool:** `pytest --durations=10` shows 10 slowest tests.

**Action:** Tests above X seconds (e.g., 1s for unit, 5s for integration) for review - can they be sped up?

**CI:** Add `--durations=10` to CI to see trends.
