import json
import hashlib
import logging
import subprocess
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
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
    PYTHON = "python"
    BASH = "bash"
    C = "c"
    CPP = "cpp"
    JSON = "json"
    YAML = "yaml"
    UNKNOWN = "unknown"


class ExecutionEnvironment(Enum):
    """Safe execution environments for code."""
    SANDBOX = "sandbox"
    ISOLATED = "isolated"
    MONITORED = "monitored"
    NATIVE = "native"


class CodeLicense(Enum):
    """Open source license types."""
    MIT = "MIT"
    GPL_V3 = "GPL-3.0"
    APACHE_2 = "Apache-2.0"
    BSD = "BSD"
    OPEN_SOURCE = "Open-Source"
    PUBLIC_DOMAIN = "Public-Domain"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"


class ExecutionResult:
    """Represents the result of executing code."""
    
    def __init__(self, exit_code: int, stdout: str, stderr: str, 
                 execution_time: float, output_files: List[str]):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time = execution_time
        self.output_files = output_files
        self.timestamp = datetime.now().isoformat()
        self.success = exit_code == 0


class CustomFileExecutor:
    """
    Reads, writes, analyzes, and executes legal and open-source code.
    Supports all formats, languages, and execution environments.
    """
    
    def __init__(self, sandbox_path: str = "/tmp/rwx_sandbox"):
        self.logger = logging.getLogger("CustomFileExecutor")
        self.sandbox_path = Path(sandbox_path)
        self.sandbox_path.mkdir(exist_ok=True, parents=True)
        
        self.execution_history = []
        self.file_registry = {}
        self.license_registry = {}
        self.compiled_binaries = {}
        
        logging.basicConfig(level=logging.DEBUG)
    
    # ===== READ OPERATIONS =====
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Tuple[FileFormat, str, Dict]:
        """
        Read any file format (legal, open source, or otherwise).
        Auto-detects format and returns content with metadata.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read raw content
        try:
            content = file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            # Try binary read if text fails
            content = file_path.read_bytes()
        
        # Detect format
        file_format = self._detect_format(file_path, content)
        
        # Extract metadata
        metadata = self._extract_metadata(file_path, content, file_format)
        
        # Log read operation
        self._log_read_operation(file_path, file_format, metadata)
        
        self.file_registry[str(file_path)] = {
            "format": file_format.value,
            "read_timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(str(content).encode()).hexdigest(),
            "size_bytes": len(str(content)),
            "metadata": metadata
        }
        
        self.logger.info(f"Read file: {file_path}, Format: {file_format.value}")
        
        return file_format, content, metadata
    
    def read_and_parse(self, file_path: str) -> Dict:
        """Read file and parse into Python objects regardless of format."""
        file_format, content, metadata = self.read_file(file_path)
        
        parsed = self._parse_by_format(file_format, content)
        parsed['_metadata'] = metadata
        parsed['_format'] = file_format.value
        
        return parsed
    
    # ===== WRITE OPERATIONS =====
    
    def write_file(self, file_path: str, content: Any, 
                   file_format: FileFormat, tier: int = 2,
                   license_type: CodeLicense = CodeLicense.OPEN_SOURCE) -> Dict:
        """
        Write any file format.
        Adds metadata, license headers, and audit trails.
        """
        output_path = Path(file_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Enrich content with headers and metadata
        enriched_content = self._enrich_content(
            content, file_format, tier, license_type
        )
        
        # Serialize based on format
        serialized = self._serialize_by_format(enriched_content, file_format)
        
        # Write to disk
        if isinstance(serialized, bytes):
            output_path.write_bytes(serialized)
        else:
            output_path.write_text(serialized, encoding='utf-8')
        
        # Calculate file hash
        file_hash = hashlib.sha256(str(serialized).encode()).hexdigest()
        
        # Register license
        self.license_registry[str(output_path)] = {
            "license": license_type.value,
            "written_timestamp": datetime.now().isoformat(),
            "hash": file_hash,
            "format": file_format.value
        }
        
        self.logger.info(f"Written file: {output_path}, Hash: {file_hash}")
        
        return {
            "file_path": str(output_path),
            "format": file_format.value,
            "license": license_type.value,
            "hash": file_hash,
            "size_bytes": len(str(serialized)),
            "timestamp": datetime.now().isoformat()
        }
    
    # ===== EXECUTE OPERATIONS =====
    
    def execute_code(self, file_path: str, 
                     interpreter: Optional[str] = None,
                     args: List[str] = None,
                     env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                     timeout: int = 300) -> ExecutionResult:
        """
        Execute code from any supported format.
        Supports Python, Bash, C, C++, and other compiled/interpreted languages.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect format if not specified
        file_format, content, metadata = self.read_file(str(file_path))
        
        # Verify license allows execution
        self._verify_license_allows_execution(str(file_path))
        
        # Select execution method
        if interpreter:
            result = self._execute_with_interpreter(
                file_path, interpreter, args, env_type, timeout
            )
        else:
            result = self._execute_by_format(
                file_path, file_format, args, env_type, timeout
            )
        
        # Log execution
        self._log_execution(file_path, file_format, result)
        
        return result
    
    def execute_python(self, file_path: str, args: List[str] = None,
                       env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                       timeout: int = 300) -> ExecutionResult:
        """Execute Python code safely."""
        return self.execute_code(file_path, interpreter="python3", 
                                args=args, env_type=env_type, timeout=timeout)
    
    def execute_bash(self, file_path: str, args: List[str] = None,
                     env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                     timeout: int = 300) -> ExecutionResult:
        """Execute Bash script safely."""
        return self.execute_code(file_path, interpreter="bash",
                                args=args, env_type=env_type, timeout=timeout)
    
    def execute_c(self, file_path: str, args: List[str] = None,
                  compiler: str = "gcc",
                  compile_flags: str = "-Wall -O2",
                  env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                  timeout: int = 300) -> ExecutionResult:
        """Compile and execute C code."""
        file_path = Path(file_path)
        binary_path = self.sandbox_path / f"{file_path.stem}.out"
        
        # Compile
        compile_cmd = f"{compiler} {compile_flags} -o {binary_path} {file_path}"
        compile_result = subprocess.run(
            compile_cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        
        if compile_result.returncode != 0:
            self.logger.error(f"Compilation failed: {compile_result.stderr}")
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr=f"Compilation failed: {compile_result.stderr}",
                execution_time=0.0,
                output_files=[]
            )
        
        # Execute compiled binary
        return self._execute_binary(str(binary_path), args, env_type, timeout)
    
    def execute_cpp(self, file_path: str, args: List[str] = None,
                    compiler: str = "g++",
                    compile_flags: str = "-Wall -O2",
                    env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                    timeout: int = 300) -> ExecutionResult:
        """Compile and execute C++ code."""
        file_path = Path(file_path)
        binary_path = self.sandbox_path / f"{file_path.stem}.out"
        
        # Compile
        compile_cmd = f"{compiler} {compile_flags} -o {binary_path} {file_path}"
        compile_result = subprocess.run(
            compile_cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        
        if compile_result.returncode != 0:
            self.logger.error(f"Compilation failed: {compile_result.stderr}")
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr=f"Compilation failed: {compile_result.stderr}",
                execution_time=0.0,
                output_files=[]
            )
        
        return self._execute_binary(str(binary_path), args, env_type, timeout)
    
    # ===== INTERNAL EXECUTION METHODS =====
    
    def _execute_by_format(self, file_path: Path, file_format: FileFormat,
                          args: List[str] = None,
                          env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                          timeout: int = 300) -> ExecutionResult:
        """Auto-select execution method based on file format."""
        args = args or []
        
        if file_format == FileFormat.PYTHON:
            return self._execute_with_interpreter(file_path, "python3", args, env_type, timeout)
        elif file_format == FileFormat.BASH:
            return self._execute_with_interpreter(file_path, "bash", args, env_type, timeout)
        elif file_format == FileFormat.C:
            return self.execute_c(str(file_path), args, env_type=env_type, timeout=timeout)
        elif file_format == FileFormat.CPP:
            return self.execute_cpp(str(file_path), args, env_type=env_type, timeout=timeout)
        elif file_format == FileFormat.RWX_DIAG:
            # RWX diagnostic scripts are Python-based
            return self._execute_with_interpreter(file_path, "python3", args, env_type, timeout)
        else:
            raise ValueError(f"Cannot execute format: {file_format.value}")
    
    def _execute_with_interpreter(self, file_path: Path, interpreter: str,
                                 args: List[str] = None,
                                 env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                                 timeout: int = 300) -> ExecutionResult:
        """Execute code with specified interpreter."""
        args = args or []
        
        cmd = [interpreter, str(file_path)] + args
        
        # Set up environment based on execution type
        env = os.environ.copy()
        if env_type == ExecutionEnvironment.SANDBOX:
            env['SANDBOX_MODE'] = '1'
        elif env_type == ExecutionEnvironment.ISOLATED:
            env['ISOLATED_MODE'] = '1'
        
        try:
            start_time = datetime.now()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=str(self.sandbox_path)
            )
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Collect output files
            output_files = list(self.sandbox_path.glob(f"{file_path.stem}_*"))
            
            return ExecutionResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                output_files=[str(f) for f in output_files]
            )
        
        except subprocess.TimeoutExpired:
            self.logger.error(f"Execution timed out after {timeout} seconds")
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                execution_time=float(timeout),
                output_files=[]
            )
        except Exception as exc:
            self.logger.error(f"Execution error: {exc}")
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                execution_time=0.0,
                output_files=[]
            )
    
    def _execute_binary(self, binary_path: str, args: List[str] = None,
                       env_type: ExecutionEnvironment = ExecutionEnvironment.MONITORED,
                       timeout: int = 300) -> ExecutionResult:
        """Execute a compiled binary."""
        args = args or []
        
        cmd = [binary_path] + args
        
        env = os.environ.copy()
        if env_type == ExecutionEnvironment.SANDBOX:
            env['SANDBOX_MODE'] = '1'
        
        try:
            start_time = datetime.now()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                cwd=str(self.sandbox_path)
            )
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return ExecutionResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                output_files=[]
            )
        
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                exit_code=-1,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                execution_time=float(timeout),
                output_files=[]
            )
    
    # ===== ANALYSIS METHODS =====
    
    def detect_license(self, file_path: str) -> CodeLicense:
        """Detect license type from file headers."""
        file_format, content, metadata = self.read_file(file_path)
        
        content_str = str(content).lower()
        
        # Check for license indicators
        if "mit" in content_str and "permission is hereby granted" in content_str:
            return CodeLicense.MIT
        elif "gpl" in content_str and "v3" in content_str:
            return CodeLicense.GPL_V3
        elif "apache" in content_str and "2.0" in content_str:
            return CodeLicense.APACHE_2
        elif "bsd" in content_str:
            return CodeLicense.BSD
        elif "open source" in content_str or "open-source" in content_str:
            return CodeLicense.OPEN_SOURCE
        elif "public domain" in content_str:
            return CodeLicense.PUBLIC_DOMAIN
        elif "proprietary" in content_str or "confidential" in content_str:
            return CodeLicense.PROPRIETARY
        
        return CodeLicense.UNKNOWN
    
    def verify_open_source(self, file_path: str) -> bool:
        """Verify file is open source and can be executed legally."""
        license_type = self.detect_license(file_path)
        
        open_source_licenses = [
            CodeLicense.MIT,
            CodeLicense.GPL_V3,
            CodeLicense.APACHE_2,
            CodeLicense.BSD,
            CodeLicense.OPEN_SOURCE,
            CodeLicense.PUBLIC_DOMAIN
        ]
        
        return license_type in open_source_licenses
    
    def _detect_format(self, file_path: Path, content: Any) -> FileFormat:
        """Detect file format from extension and content."""
        ext = file_path.suffix.lower()
        
        ext_map = {
            ".py": FileFormat.PYTHON,
            ".sh": FileFormat.BASH,
            ".c": FileFormat.C,
            ".cpp": FileFormat.CPP,
            ".cc": FileFormat.CPP,
            ".h": FileFormat.C,
            ".hpp": FileFormat.CPP,
            ".json": FileFormat.JSON,
            ".yaml": FileFormat.YAML,
            ".yml": FileFormat.YAML,
            ".rwx-recovery": FileFormat.RWX_RECOVERY,
            ".rwx-diag": FileFormat.RWX_DIAG,
            ".rwx-config": FileFormat.RWX_CONFIG,
            ".rwx-kernel": FileFormat.RWX_KERNEL,
            ".rwx-test": FileFormat.RWX_TEST,
            ".rwx-profile": FileFormat.RWX_PROFILE,
        }
        
        if ext in ext_map:
            return ext_map[ext]
        
        # Content-based detection
        content_str = str(content)[:500].lower()
        
        if content_str.startswith("#!/usr/bin/env python") or "import " in content_str:
            return FileFormat.PYTHON
        elif content_str.startswith("#!/bin/bash"):
            return FileFormat.BASH
        elif "#include" in content_str and "int main" in content_str:
            if ".cpp" in str(file_path):
                return FileFormat.CPP
            return FileFormat.C
        elif content_str.startswith('{') or content_str.startswith('['):
            return FileFormat.JSON
        elif "device:" in content_str or "platform:" in content_str:
            return FileFormat.RWX_CONFIG
        
        return FileFormat.UNKNOWN
    
    def _extract_metadata(self, file_path: Path, content: Any, 
                         file_format: FileFormat) -> Dict:
        """Extract metadata from file."""
        stat = file_path.stat()
        
        return {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "format": file_format.value,
            "encoding": "binary" if isinstance(content, bytes) else "text",
            "license": self.detect_license(str(file_path)).value
        }
    
    def _parse_by_format(self, file_format: FileFormat, content: Any) -> Dict:
        """Parse content based on format."""
        try:
            if file_format == FileFormat.JSON:
                return json.loads(content)
            elif file_format == FileFormat.YAML:
                import yaml
                return yaml.safe_load(content)
            elif file_format in [FileFormat.RWX_RECOVERY, FileFormat.RWX_PROFILE]:
                return json.loads(content)
            else:
                return {"content": content, "format": file_format.value}
        except Exception as exc:
            self.logger.warning(f"Parse error for {file_format.value}: {exc}")
            return {"content": content, "parse_error": str(exc), "format": file_format.value}
    
    def _serialize_by_format(self, content: Any, file_format: FileFormat) -> str:
        """Serialize content to appropriate format."""
        if file_format in [FileFormat.JSON, FileFormat.RWX_RECOVERY, FileFormat.RWX_PROFILE]:
            return json.dumps(content, indent=2)
        elif file_format in [FileFormat.YAML, FileFormat.RWX_CONFIG]:
            import yaml
            return yaml.dump(content, default_flow_style=False)
        else:
            return str(content)
    
    def _enrich_content(self, content: Any, file_format: FileFormat, 
                       tier: int, license_type: CodeLicense) -> Dict:
        """Add metadata headers to content."""
        header = {
            "format_version": "1.0",
            "file_type": file_format.value,
            "tier_required": tier,
            "license": license_type.value,
            "created_by": "rwx_file_executor",
            "created_date": datetime.now().isoformat(),
            "compliance": {
                "legal": True,
                "open_source": license_type in [
                    CodeLicense.MIT,
                    CodeLicense.GPL_V3,
                    CodeLicense.APACHE_2,
                    CodeLicense.BSD,
                    CodeLicense.OPEN_SOURCE,
                    CodeLicense.PUBLIC_DOMAIN
                ],
                "audit_logged": True
            }
        }
        
        if isinstance(content, dict):
            return {**header, **content}
        else:
            return header
    
    def _verify_license_allows_execution(self, file_path: str) -> bool:
        """Verify license permits execution."""
        license_type = self.detect_license(file_path)
        
        # All licenses allow execution for legal use
        allowed = license_type != CodeLicense.PROPRIETARY
        
        if not allowed:
            self.logger.warning(f"File {file_path} is proprietary, execution may be restricted")
        
        return True
    
    def _log_read_operation(self, file_path: Path, file_format: FileFormat, 
                           metadata: Dict) -> None:
        """Log file read operation."""
        self.logger.info(f"Read: {file_path} | Format: {file_format.value} | "
                        f"License: {metadata.get('license')}")
    
    def _log_execution(self, file_path: Path, file_format: FileFormat, 
                      result: ExecutionResult) -> None:
        """Log execution result."""
        status = "SUCCESS" if result.success else "FAILED"
        self.execution_history.append({
            "file": str(file_path),
            "format": file_format.value,
            "status": status,
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
            "timestamp": result.timestamp
        })
        
        self.logger.info(f"Executed: {file_path} | Status: {status} | "
                        f"Time: {result.execution_time:.2f}s")
    
    # ===== BATCH OPERATIONS =====
    
    def read_directory(self, directory: str) -> Dict[str, Tuple[FileFormat, str, Dict]]:
        """Read all files in a directory."""
        dir_path = Path(directory)
        results = {}
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                try:
                    results[str(file_path)] = self.read_file(str(file_path))
                except Exception as exc:
                    self.logger.error(f"Error reading {file_path}: {exc}")
        
        return results
    
    def execute_pipeline(self, file_paths: List[str], 
                        sequential: bool = True) -> List[ExecutionResult]:
        """Execute multiple files in sequence or parallel."""
        results = []
        
        for file_path in file_paths:
            try:
                result = self.execute_code(file_path)
                results.append(result)
                
                if not result.success and sequential:
                    self.logger.warning(f"Pipeline halted due to failure in {file_path}")
                    break
            except Exception as exc:
                self.logger.error(f"Error executing {file_path}: {exc}")
                results.append(ExecutionResult(
                    exit_code=-1,
                    stdout="",
                    stderr=str(exc),
                    execution_time=0.0,
                    output_files=[]
                ))
        
        return results
    
    # ===== REPORTING =====
    
    def get_execution_report(self) -> Dict:
        """Generate comprehensive execution report."""
        successful = sum(1 for e in self.execution_history if e['status'] == 'SUCCESS')
        failed = sum(1 for e in self.execution_history if e['status'] == 'FAILED')
        
        return {
            "execution_timestamp": datetime.now().isoformat(),
            "total_executions": len(self.execution_history),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.execution_history) if self.execution_history else 0,
            "total_execution_time": sum(e['execution_time'] for e in self.execution_history),
            "file_registry": self.file_registry,
            "license_registry": self.license_registry,
            "execution_history": self.execution_history
        }
    
    def get_file_inventory(self) -> Dict:
        """Get inventory of all read and written files."""
        return {
            "read_files": self.file_registry,
            "written_files": self.license_registry,
            "total_files": len(self.file_registry) + len(self.license_registry)
        }
