import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from pathlib import Path


class FileFormat(Enum):
    """Supported custom file formats."""
    RWX_RECOVERY = "rwx-recovery"
    RWX_DIAG = "rwx-diag"
    RWX_CONFIG = "rwx-config"
    RWX_KERNEL = "rwx-kernel"
    RWX_TEST = "rwx-test"
    RWX_PROFILE = "rwx-profile"
    RWX_SDK = "rwx-sdk"
    UNKNOWN = "unknown"


class ProblemSeverity(Enum):
    """Problem severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DetectedProblem:
    """Represents a problem detected in a custom file or device state."""
    
    def __init__(self, problem_id: str, severity: ProblemSeverity, 
                 description: str, affected_component: str, 
                 root_cause: str, suggested_fix: str):
        self.problem_id = problem_id
        self.severity = severity
        self.description = description
        self.affected_component = affected_component
        self.root_cause = root_cause
        self.suggested_fix = suggested_fix
        self.timestamp = datetime.now().isoformat()


class CustomFileAnalyzer:
    """Analyzes custom files (both good and bad formats) to detect problems and generate fixes."""
    
    def __init__(self):
        self.logger = logging.getLogger("CustomFileAnalyzer")
        self.detected_problems = []
        self.generated_fixes = []
        self.file_inventory = {}
        
    def read_file_format(self, file_path: str) -> Tuple[FileFormat, Dict]:
        """
        Read and parse any custom file format (good or bad).
        Returns the format type and parsed content.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8')
        file_ext = file_path.suffix.lower()
        
        # Try to detect format by extension or content
        detected_format = self._detect_format(file_ext, content)
        parsed_content = self._parse_content(detected_format, content)
        
        self.logger.info(f"Read file: {file_path}, Format: {detected_format.value}")
        self.file_inventory[file_path.name] = {
            "format": detected_format.value,
            "read_timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(content.encode()).hexdigest(),
            "size_bytes": len(content)
        }
        
        return detected_format, parsed_content
    
    def write_custom_file(self, file_path: str, content: Dict, 
                         file_format: FileFormat, tier: int) -> str:
        """
        Write a custom file in the specified format.
        Adds metadata, audit headers, and compliance markers.
        """
        # Add standard header to all custom files
        enriched_content = self._add_file_header(content, file_format, tier)
        
        # Serialize based on format
        serialized = self._serialize_format(enriched_content, file_format)
        
        # Write to disk
        output_path = Path(file_path)
        output_path.write_text(serialized, encoding='utf-8')
        
        file_hash = hashlib.sha256(serialized.encode()).hexdigest()
        self.logger.info(f"Written file: {file_path}, Hash: {file_hash}")
        
        return file_hash
    
    def analyze_for_problems(self, file_path: str) -> List[DetectedProblem]:
        """
        Analyze a custom file for problems, issues, or misconfigurations.
        Scans both good and malformed files to identify root causes.
        """
        try:
            file_format, content = self.read_file_format(file_path)
        except Exception as exc:
            self.logger.error(f"Error reading file: {exc}")
            return [DetectedProblem(
                "PARSE_ERROR",
                ProblemSeverity.CRITICAL,
                f"File could not be parsed: {exc}",
                "file_format",
                "Invalid or corrupted file structure",
                "Rebuild file with valid format or provide correct file"
            )]
        
        problems = []
        
        # Run format-specific analysis
        if file_format == FileFormat.RWX_RECOVERY:
            problems.extend(self._analyze_recovery_profile(content))
        elif file_format == FileFormat.RWX_DIAG:
            problems.extend(self._analyze_diag_script(content))
        elif file_format == FileFormat.RWX_CONFIG:
            problems.extend(self._analyze_config_file(content))
        elif file_format == FileFormat.RWX_KERNEL:
            problems.extend(self._analyze_kernel_file(content))
        elif file_format == FileFormat.RWX_TEST:
            problems.extend(self._analyze_test_suite(content))
        elif file_format == FileFormat.RWX_PROFILE:
            problems.extend(self._analyze_performance_profile(content))
        
        # Run generic analysis
        problems.extend(self._analyze_generic_issues(content, file_format))
        
        self.detected_problems.extend(problems)
        return problems
    
    def generate_fix_code(self, problem: DetectedProblem, 
                         file_format: FileFormat) -> str:
        """
        Generate custom fix code to resolve a detected problem.
        Returns code in the appropriate language/format.
        """
        fix_code = ""
        
        if file_format == FileFormat.RWX_RECOVERY:
            fix_code = self._generate_recovery_fix(problem)
        elif file_format == FileFormat.RWX_DIAG:
            fix_code = self._generate_diag_fix(problem)
        elif file_format == FileFormat.RWX_CONFIG:
            fix_code = self._generate_config_fix(problem)
        elif file_format == FileFormat.RWX_KERNEL:
            fix_code = self._generate_kernel_fix(problem)
        elif file_format == FileFormat.RWX_TEST:
            fix_code = self._generate_test_fix(problem)
        elif file_format == FileFormat.RWX_PROFILE:
            fix_code = self._generate_profile_fix(problem)
        
        # Wrap with audit and compliance headers
        fix_code = self._wrap_fix_with_audit(fix_code, problem, file_format)
        
        self.generated_fixes.append({
            "problem_id": problem.problem_id,
            "fix_generated": datetime.now().isoformat(),
            "format": file_format.value,
            "code_hash": hashlib.sha256(fix_code.encode()).hexdigest()
        })
        
        return fix_code
    
    # ===== Analysis Methods =====
    
    def _detect_format(self, file_ext: str, content: str) -> FileFormat:
        """Detect file format from extension and content."""
        ext_map = {
            ".rwx-recovery": FileFormat.RWX_RECOVERY,
            ".rwx-diag": FileFormat.RWX_DIAG,
            ".rwx-config": FileFormat.RWX_CONFIG,
            ".rwx-kernel": FileFormat.RWX_KERNEL,
            ".rwx-test": FileFormat.RWX_TEST,
            ".rwx-profile": FileFormat.RWX_PROFILE,
            ".rwx-sdk": FileFormat.RWX_SDK,
        }
        
        if file_ext in ext_map:
            return ext_map[file_ext]
        
        # Fallback: try to detect from content
        if "profile_name" in content and "device_family" in content:
            return FileFormat.RWX_RECOVERY
        if "def diagnose" in content or "def test_" in content:
            return FileFormat.RWX_DIAG
        if content.strip().startswith("device:") or "device:" in content[:100]:
            return FileFormat.RWX_CONFIG
        
        return FileFormat.UNKNOWN
    
    def _parse_content(self, file_format: FileFormat, content: str) -> Dict:
        """Parse content based on detected format."""
        try:
            if file_format in [FileFormat.RWX_RECOVERY, FileFormat.RWX_PROFILE]:
                return json.loads(content)
            elif file_format == FileFormat.RWX_CONFIG:
                import yaml
                return yaml.safe_load(content)
            else:
                return {"raw_content": content, "format": file_format.value}
        except Exception as exc:
            self.logger.warning(f"Could not parse content as {file_format.value}: {exc}")
            return {"raw_content": content, "parse_error": str(exc)}
    
    def _analyze_recovery_profile(self, content: Dict) -> List[DetectedProblem]:
        """Analyze recovery profile format for problems."""
        problems = []
        
        # Check required fields
        required_fields = ["profile_name", "device_family", "operations"]
        for field in required_fields:
            if field not in content:
                problems.append(DetectedProblem(
                    f"MISSING_FIELD_{field}",
                    ProblemSeverity.HIGH,
                    f"Missing required field: {field}",
                    "recovery_profile_structure",
                    f"Field '{field}' is mandatory for recovery profiles",
                    f"Add '{field}' field to the profile JSON"
                ))
        
        # Check operations for safety
        operations = content.get("operations", [])
        if not operations:
            problems.append(DetectedProblem(
                "NO_OPERATIONS",
                ProblemSeverity.MEDIUM,
                "Recovery profile has no operations defined",
                "recovery_operations",
                "Profile has empty operations list",
                "Add at least one safe operation to the profile"
            ))
        
        for op in operations:
            if not isinstance(op, dict):
                problems.append(DetectedProblem(
                    "INVALID_OPERATION",
                    ProblemSeverity.HIGH,
                    f"Operation is not a dictionary: {op}",
                    "operation_format",
                    "Operations must be structured as dictionaries",
                    "Ensure each operation is properly formatted as a dict"
                ))
            elif "action" not in op:
                problems.append(DetectedProblem(
                    "MISSING_ACTION",
                    ProblemSeverity.HIGH,
                    f"Operation missing 'action' field",
                    "operation_structure",
                    "Each operation must define an action",
                    "Add 'action' key to each operation"
                ))
            elif not op.get("safe", True):
                problems.append(DetectedProblem(
                    "UNSAFE_OPERATION",
                    ProblemSeverity.CRITICAL,
                    f"Operation marked as unsafe: {op.get('action')}",
                    "operation_safety",
                    "Unsafe operations detected in recovery profile",
                    "Mark operation as safe=true or remove it"
                ))
        
        # Check for signature
        if "signing_key" not in content:
            problems.append(DetectedProblem(
                "NO_SIGNATURE",
                ProblemSeverity.MEDIUM,
                "Recovery profile has no signing key",
                "file_signature",
                "File is not cryptographically signed",
                "Add signing_key field before deployment"
            ))
        
        return problems
    
    def _analyze_diag_script(self, content: Dict) -> List[DetectedProblem]:
        """Analyze diagnostic script for problems."""
        problems = []
        raw = content.get("raw_content", "")
        
        # Check for dangerous functions
        dangerous_patterns = [
            ("import os", "Direct OS access"),
            ("exec(", "Dynamic code execution"),
            ("eval(", "Dynamic evaluation"),
            ("__import__", "Runtime imports"),
            ("sys.exit(", "Uncontrolled exit"),
        ]
        
        for pattern, desc in dangerous_patterns:
            if pattern in raw:
                problems.append(DetectedProblem(
                    f"DANGEROUS_PATTERN_{pattern}",
                    ProblemSeverity.HIGH,
                    f"Diagnostic script contains potentially dangerous pattern: {pattern}",
                    "script_safety",
                    desc,
                    f"Replace or remove '{pattern}' with safe alternatives"
                ))
        
        # Check for required headers
        if "def " not in raw:
            problems.append(DetectedProblem(
                "NO_FUNCTIONS",
                ProblemSeverity.MEDIUM,
                "Diagnostic script has no function definitions",
                "script_structure",
                "Script lacks proper function structure",
                "Define diagnostic functions in the script"
            ))
        
        return problems
    
    def _analyze_config_file(self, content: Dict) -> List[DetectedProblem]:
        """Analyze configuration file for problems."""
        problems = []
        
        # Check device specification
        if "device" not in content:
            problems.append(DetectedProblem(
                "NO_DEVICE_SPEC",
                ProblemSeverity.HIGH,
                "Configuration missing device specification",
                "config_device",
                "No target device defined",
                "Add 'device:' field with device model"
            ))
        
        # Check safety checks section
        safety_checks = content.get("safety_checks", [])
        if not safety_checks:
            problems.append(DetectedProblem(
                "NO_SAFETY_CHECKS",
                ProblemSeverity.MEDIUM,
                "Configuration has no safety checks defined",
                "safety_mechanisms",
                "Configuration lacks safety validation",
                "Add safety_checks section to configuration"
            ))
        
        # Check operations
        operations = content.get("operations", [])
        for op in operations:
            if not op.get("safe_boundary"):
                problems.append(DetectedProblem(
                    f"MISSING_SAFE_BOUNDARY_{op.get('name')}",
                    ProblemSeverity.MEDIUM,
                    f"Operation '{op.get('name')}' missing safe_boundary designation",
                    "operation_boundary",
                    "Operation safety boundary not defined",
                    "Add safe_boundary field to operation"
                ))
        
        return problems
    
    def _analyze_kernel_file(self, content: Dict) -> List[DetectedProblem]:
        """Analyze kernel file for problems."""
        problems = []
        raw = content.get("raw_content", "")
        
        # Check for required safety verification
        if "rwx_api_verify_dev_registration()" not in raw:
            problems.append(DetectedProblem(
                "NO_DEV_VERIFICATION",
                ProblemSeverity.CRITICAL,
                "Kernel missing device registration verification",
                "kernel_security",
                "Kernel does not verify it's running on a registered dev device",
                "Add rwx_api_verify_dev_registration() call at boot"
            ))
        
        # Check for bootloader modification attempts
        if "bootloader" in raw.lower() and "modify" in raw.lower():
            problems.append(DetectedProblem(
                "BOOTLOADER_MODIFICATION",
                ProblemSeverity.CRITICAL,
                "Kernel contains bootloader modification code",
                "kernel_security",
                "Bootloader should not be modified by debug kernel",
                "Remove bootloader modification code from kernel"
            ))
        
        return problems
    
    def _analyze_test_suite(self, content: Dict) -> List[DetectedProblem]:
        """Analyze test suite for problems."""
        problems = []
        raw = content.get("raw_content", "")
        
        if "class " not in raw or "def test_" not in raw:
            problems.append(DetectedProblem(
                "INVALID_TEST_STRUCTURE",
                ProblemSeverity.MEDIUM,
                "Test suite missing proper class/method structure",
                "test_structure",
                "Tests not properly organized",
                "Structure tests as class with test_* methods"
            ))
        
        # Check for rollback/cleanup
        if "tearDown" not in raw and "cleanup" not in raw.lower():
            problems.append(DetectedProblem(
                "NO_CLEANUP",
                ProblemSeverity.MEDIUM,
                "Test suite missing cleanup/tearDown method",
                "test_cleanup",
                "Tests don't clean up after themselves",
                "Add tearDown or cleanup method to test suite"
            ))
        
        return problems
    
    def _analyze_performance_profile(self, content: Dict) -> List[DetectedProblem]:
        """Analyze performance profile for problems."""
        problems = []
        
        # Check device serial
        if "device_serial" not in content:
            problems.append(DetectedProblem(
                "NO_DEVICE_SERIAL",
                ProblemSeverity.HIGH,
                "Performance profile missing device serial number",
                "profile_device",
                "Profile not bound to specific device",
                "Add device_serial field to profile"
            ))
        
        # Check customizations are reasonable
        customizations = content.get("customizations", {})
        for component, settings in customizations.items():
            if settings.get("override_clock"):
                # Check if clock speed is in reasonable range
                freq = settings.get("clock_frequency_mhz", 0)
                if freq < 100 or freq > 5000:
                    problems.append(DetectedProblem(
                        f"UNREASONABLE_CLOCK_{component}",
                        ProblemSeverity.HIGH,
                        f"Clock speed for {component} is unreasonable: {freq} MHz",
                        "customization_validity",
                        f"Clock speed {freq} MHz is outside normal range",
                        f"Set {component} clock to realistic value (100-5000 MHz)"
                    ))
        
        return problems
    
    def _analyze_generic_issues(self, content: Dict, 
                               file_format: FileFormat) -> List[DetectedProblem]:
        """Analyze common issues across all file types."""
        problems = []
        
        # Check for audit compliance
        if file_format != FileFormat.UNKNOWN:
            if "audit" not in content and "audit_log" not in content:
                problems.append(DetectedProblem(
                    "NO_AUDIT_CONFIG",
                    ProblemSeverity.LOW,
                    f"{file_format.value} file missing audit configuration",
                    "audit_compliance",
                    "File doesn't enable audit logging",
                    "Add audit section with logging configuration"
                ))
        
        # Check for timestamp
        if "timestamp" not in content and "created_date" not in content:
            problems.append(DetectedProblem(
                "NO_TIMESTAMP",
                ProblemSeverity.LOW,
                f"{file_format.value} file missing timestamp",
                "metadata",
                "File creation time not recorded",
                "Add timestamp field to file metadata"
            ))
        
        return problems
    
    # ===== Fix Generation Methods =====
    
    def _generate_recovery_fix(self, problem: DetectedProblem) -> str:
        """Generate fix code for recovery profile problems."""
        fix = f"""
// Fix for: {problem.problem_id}
// Problem: {problem.description}
// Root Cause: {problem.root_cause}

{{"
  "format_version": "1.0",
  "file_type": "recovery_profile",
  "tier_required": 2,
  "safety_boundary": "maintenance",
  "device_compatibility": ["xbox-series-s", "xbox-series-x"],
  "created_by": "ai_fix_generator",
  "created_date": "{datetime.now().isoformat()}",
  "problem_fixed": "{problem.problem_id}",
  "operations": [
    {{
      "name": "verify_device_state",
      "action": "check_device_compatibility",
      "safe": true,
      "logged": true,
      "reversible": false
    }},
    {{
      "name": "clear_error_flags",
      "action": "reset_device_errors",
      "safe": true,
      "logged": true,
      "reversible": true
    }},
    {{
      "name": "restore_factory_config",
      "action": "apply_factory_defaults",
      "safe": true,
      "logged": true,
      "reversible": true
    }}
  ],
  "audit": {{
    "enabled": true,
    "log_destination": "device_storage",
    "retention_days": 90
  }},
  "compliance": {{
    "no_security_bypass": true,
    "no_drm_circumvention": true,
    "audit_logged": true
  }}
}}
"""
        return fix
    
    def _generate_diag_fix(self, problem: DetectedProblem) -> str:
        """Generate fix code for diagnostic script problems."""
        fix = f"""
# Fix for: {problem.problem_id}
# Problem: {problem.description}
# Root Cause: {problem.root_cause}

import rwx_api
import logging
from datetime import datetime

# Audit logger
audit_logger = logging.getLogger('rwx_diag_audit')
audit_logger.setLevel(logging.DEBUG)

def initialize_diagnostics():
    \"\"\"Initialize diagnostic environment safely.\"\"\"
    audit_logger.info(f"Diagnostics initialized at {{datetime.now()}}")
    rwx_api.verify_tier_authorization(2)
    rwx_api.verify_device_safe_mode()

def diagnose_problem():
    \"\"\"Diagnose the problem: {problem.affected_component}\"\"\"
    try:
        # Step 1: Verify device state
        device_state = rwx_api.read_device_state()
        audit_logger.info(f"Device state: {{device_state}}")
        
        # Step 2: Run component diagnostics
        results = rwx_api.diagnose_component("{problem.affected_component}")
        audit_logger.info(f"Diagnostics results: {{results}}")
        
        # Step 3: Generate remediation steps
        remediation = generate_remediation(results)
        return remediation
    except Exception as exc:
        audit_logger.error(f"Diagnostic error: {{exc}}")
        raise

def generate_remediation(results):
    \"\"\"Generate fix based on diagnostic results.\"\"\"
    if results['status'] == 'FAILED':
        return {{
            "action": "apply_fix",
            "component": "{problem.affected_component}",
            "fix_type": "configuration_reset",
            "safe": True
        }}
    return {{"status": "no_fix_needed"}}

if __name__ == "__main__":
    initialize_diagnostics()
    fix = diagnose_problem()
    audit_logger.info(f"Remediation: {{fix}}")
"""
        return fix
    
    def _generate_config_fix(self, problem: DetectedProblem) -> str:
        """Generate fix code for configuration file problems."""
        fix = f"""
# Fix for: {problem.problem_id}
# Problem: {problem.description}

device: xbox-series-s-auto-repaired
tier: 2
purpose: {problem.affected_component}-repair
created_date: {datetime.now().isoformat()}
auto_generated_fix: true

safety_checks:
  - verify_device_family
  - check_firmware_version
  - validate_thermal_sensors
  - check_power_rails

operations:
  - name: diagnose_component
    action: read_{problem.affected_component}_state
    safe_boundary: maintenance
    rollback: enabled
    audit: verbose
  
  - name: apply_fix
    action: repair_{problem.affected_component}
    safe_boundary: maintenance
    rollback: enabled
    audit: verbose
  
  - name: verify_fix
    action: validate_{problem.affected_component}
    safe_boundary: maintenance
    rollback: disabled
    audit: verbose

audit:
  enabled: true
  log_destination: device_storage
  retention_days: 90
  problem_fixed: "{problem.problem_id}"

restrictions:
  cannot_modify_bootloader: true
  cannot_disable_security: true
  cannot_bypass_drm: true
"""
        return fix
    
    def _generate_kernel_fix(self, problem: DetectedProblem) -> str:
        """Generate fix code for kernel problems."""
        fix = f"""
// Fix for: {problem.problem_id}
// Problem: {problem.description}

#include <rwx_api.h>
#include <rwx_audit.h>

#define RWX_SAFE_BOOT 1
#define RWX_DEV_VERIFY_REQUIRED 1

void rwx_debug_init() {{
    // Step 1: Verify device is registered for development
    if (!rwx_api_verify_dev_registration()) {{
        rwx_api_emergency_shutdown("Device not registered for dev kernel");
    }}
    
    // Step 2: Verify boot signature
    if (!rwx_api_verify_boot_signature()) {{
        rwx_api_emergency_shutdown("Boot signature verification failed");
    }}
    
    // Step 3: Initialize safe debug environment
    rwx_api_enable_safe_debug_mode();
    rwx_api_enable_audit_logging();
    
    // Step 4: Initialize specific fix for {problem.affected_component}
    rwx_audit_log("Kernel debug init: Applying fix for {problem.affected_component}");
}}

void fix_{problem.affected_component}() {{
    // Problem: {problem.description}
    // Root Cause: {problem.root_cause}
    
    rwx_audit_log("Starting fix for {problem.affected_component}");
    
    // Read current state
    struct component_state state = rwx_api_read_component_state("{problem.affected_component}");
    
    // Apply safe remediation
    if (state.error_flag) {{
        rwx_api_clear_error_flag("{problem.affected_component}");
        rwx_audit_log("{problem.affected_component} error flag cleared");
    }}
    
    // Verify fix was applied
    struct component_state new_state = rwx_api_read_component_state("{problem.affected_component}");
    if (new_state.status == COMPONENT_OK) {{
        rwx_audit_log("{problem.affected_component} repair successful");
    }} else {{
        rwx_audit_log("WARNING: {problem.affected_component} repair may have failed");
    }}
}}

int main() {{
    rwx_debug_init();
    fix_{problem.affected_component}();
    rwx_api_graceful_shutdown();
    return 0;
}}
"""
        return fix
    
    def _generate_test_fix(self, problem: DetectedProblem) -> str:
        """Generate fix code for test suite problems."""
        fix = f"""
# Fix for: {problem.problem_id}
# Problem: {problem.description}

import rwx_test_framework as rwx
import logging
from datetime import datetime

audit_logger = logging.getLogger('rwx_test_audit')

class ComponentRepairTestSuite(rwx.TestSuite):
    \"\"\"Test suite for {problem.affected_component} repair verification.\"\"\"
    
    def setUp(self):
        \"\"\"Initialize test environment.\"\"\"
        audit_logger.info(f"Test setUp: {{datetime.now()}}")
        self.device = rwx.connect_device()
        self.device.verify_safe_mode()
    
    def tearDown(self):
        \"\"\"Clean up after tests.\"\"\"
        audit_logger.info(f"Test tearDown: {{datetime.now()}}")
        self.device.reset_to_baseline()
        self.device.disconnect()
    
    def test_component_diagnostics(self):
        \"\"\"Diagnose {problem.affected_component} status.\"\"\"
        state = self.device.read_{problem.affected_component}_state()
        self.assertIsNotNone(state)
        audit_logger.info(f"Diagnostics: {{state}}")
    
    def test_apply_fix(self):
        \"\"\"Apply fix to {problem.affected_component}.\"\"\"
        # Apply remediation
        result = self.device.repair_{problem.affected_component}()
        self.assertTrue(result['success'])
        audit_logger.info(f"Fix applied: {{result}}")
    
    def test_verify_fix(self):
        \"\"\"Verify fix was successful.\"\"\"
        state = self.device.read_{problem.affected_component}_state()
        self.assertEqual(state['status'], 'OK')
        audit_logger.info(f"Verification passed: {{state}}")

if __name__ == "__main__":
    suite = ComponentRepairTestSuite()
    suite.run_all_tests()
    suite.generate_report("repair-verification.json")
"""
        return fix
    
    def _generate_profile_fix(self, problem: DetectedProblem) -> str:
        """Generate fix code for performance profile problems."""
        fix = f"""
{{
  "profile_id": "auto-generated-fix-profile",
  "device_serial": "auto-detect",
  "tier": 3,
  "created_date": "{datetime.now().isoformat()}",
  "problem_fixed": "{problem.problem_id}",
  "developer_account": "ai_system",
  "project": "Automated Repair",
  "safety_boundary": "developer_testing",
  "customizations": {{
    "diagnostic_mode": {{
      "enable_extended_logging": true,
      "enable_detailed_profiling": true,
      "capture_thermal_data": true,
      "capture_power_data": true
    }},
    "target_component": {{
      "component": "{problem.affected_component}",
      "diagnostic_level": "verbose",
      "enable_recovery": true,
      "enable_rollback": true
    }}
  }},
  "repair_steps": [
    {{
      "step": 1,
      "action": "diagnose_{problem.affected_component}",
      "verify": true,
      "rollback": true
    }},
    {{
      "step": 2,
      "action": "apply_fix_{problem.affected_component}",
      "verify": true,
      "rollback": true
    }},
    {{
      "step": 3,
      "action": "verify_repair_{problem.affected_component}",
      "verify": true,
      "rollback": false
    }}
  ],
  "restrictions": {{
    "cannot_modify_bootloader": true,
    "cannot_disable_security": true,
    "cannot_bypass_drm": true,
    "non_commercial_use_only": true,
    "no_distribution": true
  }},
  "audit": {{
    "log_all_operations": true,
    "compliance_checks": true,
    "retention_days": 180,
    "problem_fixed": "{problem.problem_id}"
  }}
}}
"""
        return fix
    
    def _wrap_fix_with_audit(self, fix_code: str, problem: DetectedProblem, 
                            file_format: FileFormat) -> str:
        """Wrap generated fix with audit and compliance headers."""
        audit_header = f"""
================================================================================
GENERATED FIX CODE
================================================================================
Problem ID:       {problem.problem_id}
Severity:         {problem.severity.value}
Description:      {problem.description}
Affected:         {problem.affected_component}
Root Cause:       {problem.root_cause}
Generated:        {datetime.now().isoformat()}
Format:           {file_format.value}

COMPLIANCE NOTICE:
- This fix is auto-generated by the RWX AI Analysis Engine
- All operations are safe-boundary compliant
- All operations will be audit-logged
- Manual review recommended before deployment
- Do NOT use to bypass security or modify protected areas
================================================================================

"""
        return audit_header + fix_code
    
    # ===== File Header Methods =====
    
    def _add_file_header(self, content: Dict, file_format: FileFormat, 
                        tier: int) -> Dict:
        """Add standard RWX header to custom files."""
        header = {
            "format_version": "1.0",
            "file_type": file_format.value,
            "tier_required": tier,
            "created_by": "rwx_ai_engine",
            "created_date": datetime.now().isoformat(),
            "compliance": {
                "no_security_bypass": True,
                "no_drm_circumvention": True,
                "audit_logged": True
            },
            "audit": {
                "enabled": True,
                "log_destination": "device_storage",
                "retention_days": 90
            }
        }
        
        # Merge headers
        enriched = {**header, **content}
        return enriched
    
    def _serialize_format(self, content: Dict, file_format: FileFormat) -> str:
        """Serialize content to appropriate format."""
        if file_format in [FileFormat.RWX_RECOVERY, FileFormat.RWX_PROFILE]:
            return json.dumps(content, indent=2)
        elif file_format == FileFormat.RWX_CONFIG:
            import yaml
            return yaml.dump(content, default_flow_style=False)
        else:
            return json.dumps(content, indent=2)
    
    def get_analysis_report(self) -> Dict:
        """Generate comprehensive analysis and fix report."""
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_files_analyzed": len(self.file_inventory),
            "total_problems_found": len(self.detected_problems),
            "total_fixes_generated": len(self.generated_fixes),
            "files_inventory": self.file_inventory,
            "problems_by_severity": {
                severity.value: len([p for p in self.detected_problems if p.severity == severity])
                for severity in ProblemSeverity
            },
            "problems": [
                {
                    "id": p.problem_id,
                    "severity": p.severity.value,
                    "description": p.description,
                    "component": p.affected_component,
                    "root_cause": p.root_cause,
                    "suggested_fix": p.suggested_fix,
                    "timestamp": p.timestamp
                }
                for p in self.detected_problems
            ],
            "generated_fixes": self.generated_fixes
        }
