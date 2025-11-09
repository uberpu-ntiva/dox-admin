#!/usr/bin/env python3
"""
Flask to FastAPI Migration Helper Tool
Automatically converts Flask routes and patterns to FastAPI equivalents
"""

import ast
import re
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RouteInfo:
    """Information about a Flask route"""
    path: str
    methods: List[str]
    function_name: str
    decorators: List[str]
    docstring: Optional[str]
    args: List[str]

class FlaskParser:
    """Parse Flask application to extract route information"""

    def __init__(self, flask_file_path: str):
        self.file_path = flask_file_path
        self.routes: List[RouteInfo] = []
        self.imports: List[str] = []
        self.app_name = None

    def parse(self) -> None:
        """Parse the Flask application file"""
        with open(self.file_path, 'r') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._parse_function(node)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        self.imports.append(f"{node.module}.{alias.name}")

    def _parse_function(self, func_node: ast.FunctionDef) -> None:
        """Parse a Flask route function"""
        decorators = []

        # Extract decorators
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                # @app.route('/path', methods=['GET'])
                if hasattr(decorator.func, 'id') and decorator.func.id == 'route':
                    path = self._extract_string_literal(decorator.args[0])
                    methods = ['GET']

                    # Extract methods if provided
                    for keyword in decorator.keywords:
                        if keyword.arg == 'methods':
                            methods = self._extract_string_list(keyword.value)

                    route_info = RouteInfo(
                        path=path,
                        methods=methods,
                        function_name=func_node.name,
                        decorators=decorators,
                        docstring=ast.get_docstring(func_node),
                        args=[arg.arg for arg in func_node.args.args]
                    )
                    self.routes.append(route_info)

    def _extract_string_literal(self, node) -> str:
        """Extract string literal from AST node"""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ""

    def _extract_string_list(self, node) -> List[str]:
        """Extract list of strings from AST node"""
        if isinstance(node, ast.List):
            return [self._extract_string_literal(elt) for elt in node.elts]
        return []

class FastAPIGenerator:
    """Generate FastAPI equivalent code from parsed Flask routes"""

    def __init__(self, routes: List[RouteInfo], imports: List[str]):
        self.routes = routes
        self.imports = imports
        self.fastapi_code = []

    def generate(self) -> str:
        """Generate FastAPI code"""
        self._add_imports()
        self._add_app_setup()
        self._add_models()
        self._add_routes()
        self._add_main_block()

        return "\n".join(self.fastapi_code)

    def _add_imports(self) -> None:
        """Add FastAPI imports"""
        fastapi_imports = [
            "from fastapi import FastAPI, Depends, HTTPException, status, Path, Query",
            "from fastapi.middleware.cors import CORSMiddleware",
            "from pydantic import BaseModel, Field",
            "from typing import Optional, Dict, Any, List",
            "import logging",
            "import time"
        ]

        # Add specific imports based on existing Flask imports
        additional_imports = self._convert_imports()

        self.fastapi_code.extend(fastapi_imports)
        if additional_imports:
            self.fastapi_code.extend(additional_imports)
        self.fastapi_code.append("")

    def _convert_imports(self) -> List[str]:
        """Convert Flask imports to FastAPI equivalents"""
        import_mapping = {
            "flask": "# Flask replaced by FastAPI",
            "flask_cors": "# Replaced by fastapi.middleware.cors.CORSMiddleware",
            "flask.json": "# Replaced by Pydantic models",
            "werkzeug": "# Replaced by FastAPI built-ins",
        }

        converted = []
        for imp in self.imports:
            if any(key in imp for key in import_mapping):
                for key, comment in import_mapping.items():
                    if key in imp:
                        converted.append(comment)
                        break
            else:
                converted.append(f"import {imp}")

        return converted

    def _add_app_setup(self) -> None:
        """Add FastAPI app setup"""
        self.fastapi_code.extend([
            "# Configure logging",
            "logging.basicConfig(level=logging.INFO)",
            "logger = logging.getLogger(__name__)",
            "",
            "# FastAPI App Instance",
            "app = FastAPI(",
            '    title="API Service",',
            '    version="1.0.0",',
            '    description="FastAPI version of the service",',
            '    docs_url="/docs",',
            '    redoc_url="/redoc"',
            ")",
            "",
            "# CORS Middleware",
            "app.add_middleware(",
            "    CORSMiddleware,",
            '    allow_origins=["*"],',
            "    allow_credentials=True,",
            '    allow_methods=["*"],',
            '    allow_headers=["*"],',
            ")",
            ""
        ])

    def _add_models(self) -> None:
        """Add Pydantic models"""
        # Basic response model
        self.fastapi_code.extend([
            "# Pydantic Models",
            "class ResponseModel(BaseModel):",
            "    success: bool",
            "    data: Optional[Dict[str, Any]] = None",
            "    error: Optional[str] = None",
            "    timestamp: float = Field(default_factory=time.time)",
            "",
            "class HealthResponse(BaseModel):",
            "    status: str",
            "    service: str",
            "    version: str",
            "    timestamp: str",
            ""
        ])

        # Add custom models based on routes
        model_names = set()
        for route in self.routes:
            model_name = self._infer_model_name(route.function_name)
            if model_name and model_name not in model_names:
                model_names.add(model_name)
                self._add_custom_model(model_name, route)

    def _infer_model_name(self, function_name: str) -> Optional[str]:
        """Infer Pydantic model name from function name"""
        name_mapping = {
            "create_": "CreateRequest",
            "update_": "UpdateRequest",
            "get_": None,  # GET requests usually don't need request models
            "delete_": None,
            "post_": "PostRequest",
            "put_": "PutRequest"
        }

        for prefix, model_name in name_mapping.items():
            if function_name.startswith(prefix):
                # Convert to PascalCase
                class_name = function_name.replace(prefix, "").replace("_", " ").title().replace(" ", "")
                return f"{class_name}{model_name}" if model_name else f"{class_name}Response"

        return None

    def _add_custom_model(self, model_name: str, route: RouteInfo) -> None:
        """Add a custom Pydantic model"""
        # Basic model structure - customize based on your needs
        self.fastapi_code.extend([
            f"class {model_name}(BaseModel):",
            f"    # TODO: Add fields based on {route.function_name} function",
            f"    # Args: {', '.join(route.args)}" if route.args else "    pass",
            ""
        ])

    def _add_routes(self) -> None:
        """Add FastAPI routes"""
        self.fastapi_code.append("# API Routes")

        for route in self.routes:
            self._add_single_route(route)

    def _add_single_route(self, route: RouteInfo) -> None:
        """Add a single FastAPI route"""
        # Convert Flask path to FastAPI path
        fastapi_path = self._convert_path(route.path)

        # Add docstring as comment if exists
        if route.docstring:
            self.fastapi_code.append(f"# {route.docstring}")

        # Add route decorators for each method
        for method in route.methods:
            if method == "GET":
                self._add_get_route(fastapi_path, route)
            elif method == "POST":
                self._add_post_route(fastapi_path, route)
            elif method == "PUT":
                self._add_put_route(fastapi_path, route)
            elif method == "DELETE":
                self._add_delete_route(fastapi_path, route)

        self.fastapi_code.append("")

    def _convert_path(self, flask_path: str) -> str:
        """Convert Flask path parameters to FastAPI format"""
        # Replace <param> with {param}
        import re
        return re.sub(r'<(\w+)>', r'{\1}', flask_path)

    def _add_get_route(self, path: str, route: RouteInfo) -> None:
        """Add a GET route"""
        model_name = self._infer_model_name(route.function_name)

        if model_name and "Response" in model_name:
            response_model = f", response_model={model_name}"
        else:
            response_model = ""

        self.fastapi_code.append(f"@app.get('{path}'{response_model})")
        self.fastapi_code.append(f"async def {route.function_name}():")
        self.fastapi_code.append(f"    # TODO: Implement {route.function_name} logic")
        self.fastapi_code.append("    pass")

    def _add_post_route(self, path: str, route: RouteInfo) -> None:
        """Add a POST route"""
        model_name = self._infer_model_name(route.function_name)

        if model_name and "Request" in model_name:
            request_param = f", request: {model_name}"
        else:
            request_param = ""

        self.fastapi_code.append(f"@app.post('{path}')")
        self.fastapi_code.append(f"async def {route.function_name}({request_param}):")
        self.fastapi_code.append(f"    # TODO: Implement {route.function_name} logic")
        self.fastapi_code.append("    pass")

    def _add_put_route(self, path: str, route: RouteInfo) -> None:
        """Add a PUT route"""
        self._add_post_route(path, route)  # Similar to POST

    def _add_delete_route(self, path: str, route: RouteInfo) -> None:
        """Add a DELETE route"""
        self._add_get_route(path, route)  # Similar to GET but for DELETE

    def _add_main_block(self) -> None:
        """Add main execution block"""
        self.fastapi_code.extend([
            "# Main execution",
            "if __name__ == '__main__':",
            "    import uvicorn",
            "    uvicorn.run(app, host='0.0.0.0', port=8000)",
            ""
        ])

def migrate_flask_to_fastapi(flask_file_path: str, output_path: str) -> None:
    """Main migration function"""
    print(f"Parsing Flask file: {flask_file_path}")

    # Parse Flask application
    parser = FlaskParser(flask_file_path)
    parser.parse()

    print(f"Found {len(parser.routes)} routes")
    for route in parser.routes:
        print(f"  {', '.join(route.methods)} {route.path} -> {route.function_name}")

    # Generate FastAPI code
    generator = FastAPIGenerator(parser.routes, parser.imports)
    fastapi_code = generator.generate()

    # Write FastAPI code
    with open(output_path, 'w') as f:
        f.write(fastapi_code)

    print(f"FastAPI code generated: {output_path}")
    print("\nNext steps:")
    print("1. Review the generated FastAPI code")
    print("2. Add missing business logic to each route")
    print("3. Add proper Pydantic models for request/response")
    print("4. Add authentication and authorization")
    print("5. Test the new FastAPI application")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python flask_to_fastapi.py <flask_file.py> <fastapi_output.py>")
        sys.exit(1)

    flask_file = sys.argv[1]
    fastapi_file = sys.argv[2]

    if not os.path.exists(flask_file):
        print(f"Error: Flask file '{flask_file}' not found")
        sys.exit(1)

    migrate_flask_to_fastapi(flask_file, fastapi_file)