#!/bin/bash
# CloudViz Installation Verification Script
# This script verifies that CloudViz installation is working correctly

set -e

# Configuration
METHOD="${1:-python}"
VERBOSE="${2:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_output="$3"
    
    log_test "Testing $test_name..."
    
    if [[ "$VERBOSE" == "true" ]]; then
        echo "Command: $test_command"
    fi
    
    if result=$(eval "$test_command" 2>&1); then
        if [[ -z "$expected_output" ]] || echo "$result" | grep -q "$expected_output"; then
            log_success "$test_name passed"
            return 0
        else
            log_error "$test_name failed - unexpected output"
            if [[ "$VERBOSE" == "true" ]]; then
                echo "Expected: $expected_output"
                echo "Got: $result"
            fi
            return 1
        fi
    else
        log_error "$test_name failed - command failed"
        if [[ "$VERBOSE" == "true" ]]; then
            echo "Error: $result"
        fi
        return 1
    fi
}

# Test network connectivity
test_connectivity() {
    local url="$1"
    local description="$2"
    
    log_test "Testing $description..."
    
    if curl -f -s -o /dev/null --max-time 10 "$url"; then
        log_success "$description is accessible"
        return 0
    else
        log_error "$description is not accessible"
        return 1
    fi
}

# Test system components
test_system_components() {
    log_info "Testing system components..."
    
    local all_passed=true
    
    # Test based on installation method
    if [[ "$METHOD" == "docker" ]]; then
        run_test "Docker" "docker --version" "Docker" || all_passed=false
        run_test "Docker Compose" "docker compose version" "Docker Compose" || all_passed=false
        run_test "Docker Service" "docker ps" || all_passed=false
    else
        run_test "Python" "python3 --version" "Python" || all_passed=false
        run_test "Pip" "pip3 --version" "pip" || all_passed=false
        run_test "Virtual Environment" "test -d venv" || all_passed=false
    fi
    
    run_test "Git" "git --version" "git" || all_passed=false
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "All system components passed"
    else
        log_error "Some system components failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Test CloudViz API
test_cloudviz_api() {
    log_info "Testing CloudViz API..."
    
    local all_passed=true
    
    # Test health endpoint
    test_connectivity "http://localhost:8000/health" "Health endpoint" || all_passed=false
    
    # Test API documentation
    test_connectivity "http://localhost:8000/docs" "API documentation" || all_passed=false
    
    # Test OpenAPI schema
    test_connectivity "http://localhost:8000/openapi.json" "OpenAPI schema" || all_passed=false
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "All API tests passed"
    else
        log_error "Some API tests failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Test CLI functionality
test_cli_functionality() {
    log_info "Testing CLI functionality..."
    
    local all_passed=true
    
    if [[ "$METHOD" == "docker" ]]; then
        # Test CLI in Docker container
        run_test "CLI Help" "docker compose exec -T cloudviz cloudviz --help" "Usage:" || all_passed=false
        run_test "CLI Version" "docker compose exec -T cloudviz cloudviz version" || all_passed=false
        run_test "Config Validation" "docker compose exec -T cloudviz cloudviz config validate" || all_passed=false
    else
        # Activate virtual environment and test CLI
        source venv/bin/activate
        run_test "CLI Help" "cloudviz --help" "Usage:" || all_passed=false
        run_test "CLI Version" "cloudviz version" || all_passed=false
        run_test "Config Validation" "cloudviz config validate" || all_passed=false
    fi
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "All CLI tests passed"
    else
        log_error "Some CLI tests failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Test database connectivity
test_database() {
    log_info "Testing database connectivity..."
    
    local all_passed=true
    
    if [[ "$METHOD" == "docker" ]]; then
        # Test database in Docker
        run_test "Database Connection" "docker compose exec -T db pg_isready -U cloudviz" "accepting connections" || all_passed=false
        run_test "Database Access" "docker compose exec -T db psql -U cloudviz -d cloudviz -c 'SELECT 1;'" || all_passed=false
    else
        # Test local database
        run_test "PostgreSQL Connection" "pg_isready -h localhost -p 5432 -U cloudviz" "accepting connections" || all_passed=false
        run_test "Database Access" "psql -h localhost -U cloudviz -d cloudviz -c 'SELECT 1;'" || all_passed=false
    fi
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "All database tests passed"
    else
        log_error "Some database tests failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Test cache connectivity
test_cache() {
    log_info "Testing cache connectivity..."
    
    local all_passed=true
    
    if [[ "$METHOD" == "docker" ]]; then
        # Test Redis in Docker
        run_test "Redis Connection" "docker compose exec -T redis redis-cli ping" "PONG" || all_passed=false
    else
        # Test local Redis
        run_test "Redis Connection" "redis-cli -h localhost -p 6379 ping" "PONG" || all_passed=false
    fi
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "All cache tests passed"
    else
        log_error "Some cache tests failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Test configuration
test_configuration() {
    log_info "Testing configuration..."
    
    local all_passed=true
    
    # Check if .env file exists
    if [[ ! -f ".env" ]]; then
        log_error ".env file not found"
        all_passed=false
    else
        log_success ".env file found"
        
        # Check for required variables
        local required_vars=("CLOUDVIZ_SECRET_KEY" "CLOUDVIZ_JWT_SECRET" "DATABASE_URL")
        
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" .env; then
                log_success "$var is configured"
            else
                log_warning "$var not found in .env file"
            fi
        done
    fi
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "Configuration tests passed"
    else
        log_warning "Some configuration checks failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Test cloud provider credentials
test_cloud_providers() {
    log_info "Testing cloud provider credentials..."
    
    # Load environment variables
    if [[ -f ".env" ]]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    # Test Azure credentials
    if [[ -n "$AZURE_TENANT_ID" && -n "$AZURE_CLIENT_ID" ]]; then
        if [[ "$AZURE_TENANT_ID" == "your-azure-tenant-id" ]]; then
            log_warning "Azure credentials not configured (using example values)"
        else
            log_success "Azure credentials configured"
        fi
    else
        log_warning "Azure credentials not found"
    fi
    
    # Test AWS credentials
    if [[ -n "$AWS_ACCESS_KEY_ID" && -n "$AWS_SECRET_ACCESS_KEY" ]]; then
        if [[ "$AWS_ACCESS_KEY_ID" == "your-aws-access-key" ]]; then
            log_warning "AWS credentials not configured (using example values)"
        else
            log_success "AWS credentials configured"
        fi
    else
        log_warning "AWS credentials not found"
    fi
    
    # Test GCP credentials
    if [[ -n "$GCP_PROJECT_ID" && -n "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
        if [[ "$GCP_PROJECT_ID" == "your-gcp-project-id" ]]; then
            log_warning "GCP credentials not configured (using example values)"
        else
            log_success "GCP credentials configured"
        fi
    else
        log_warning "GCP credentials not found"
    fi
    
    return 0
}

# Performance test
test_performance() {
    log_info "Testing performance..."
    
    local all_passed=true
    
    # Test response time
    log_test "Testing API response time..."
    local response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
    local response_time_ms=$(echo "$response_time * 1000" | bc -l | cut -d. -f1)
    
    if [[ $response_time_ms -lt 1000 ]]; then
        log_success "API response time: ${response_time_ms}ms (good)"
    elif [[ $response_time_ms -lt 5000 ]]; then
        log_warning "API response time: ${response_time_ms}ms (acceptable)"
    else
        log_error "API response time: ${response_time_ms}ms (slow)"
        all_passed=false
    fi
    
    # Test memory usage (if Docker)
    if [[ "$METHOD" == "docker" ]]; then
        log_test "Testing memory usage..."
        local memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep cloudviz | awk '{print $2}' | head -1)
        if [[ -n "$memory_usage" ]]; then
            log_success "Memory usage: $memory_usage"
        else
            log_warning "Could not determine memory usage"
        fi
    fi
    
    if [[ "$all_passed" == "true" ]]; then
        log_success "Performance tests passed"
    else
        log_error "Some performance tests failed"
    fi
    
    return $([[ "$all_passed" == "true" ]])
}

# Main verification function
main() {
    log_info "CloudViz Installation Verification"
    log_info "=================================="
    log_info "Method: $METHOD"
    log_info "Verbose: $VERBOSE"
    echo
    
    local overall_success=true
    
    # Run all test suites
    test_system_components || overall_success=false
    echo
    
    test_cloudviz_api || overall_success=false
    echo
    
    test_cli_functionality || overall_success=false
    echo
    
    test_database || overall_success=false
    echo
    
    test_cache || overall_success=false
    echo
    
    test_configuration || overall_success=false
    echo
    
    test_cloud_providers || overall_success=false
    echo
    
    test_performance || overall_success=false
    echo
    
    # Show final results
    log_info "Verification Results"
    log_info "==================="
    
    if [[ "$overall_success" == "true" ]]; then
        log_success "✓ All verification tests passed!"
        log_success "CloudViz is properly installed and configured."
        echo
        log_info "Next steps:"
        log_info "1. Configure cloud provider credentials in .env file"
        log_info "2. Test cloud connectivity: cloudviz provider test azure"
        log_info "3. Extract your first inventory: cloudviz extract azure"
        log_info "4. Generate a diagram: cloudviz render inventory.json"
    else
        log_error "✗ Some verification tests failed."
        log_error "Please check the output above for details."
        log_info "For troubleshooting help, see: wiki/Troubleshooting.md"
        exit 1
    fi
}

# Check if required tools are available
if ! command -v curl &> /dev/null; then
    log_error "curl is required but not installed. Please install curl and try again."
    exit 1
fi

if ! command -v bc &> /dev/null; then
    log_warning "bc is not installed. Some performance tests will be skipped."
fi

# Run main verification
main "$@"
