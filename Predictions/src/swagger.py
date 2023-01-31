from .routers import router
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import Response, JSONResponse
from fastapi import status
from fastapi.responses import HTMLResponse


@router.get("/predictions/openapi.json")
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="FastAPI", version=1, routes=router.routes))


@router.get("/predictions/docs")
async def get_documentation(response: Response, metadata: str = None):
    if metadata == 'easypass':
        return get_swagger_ui_html(openapi_url="/predictions/openapi.json", title="docs")

    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        html_content = """
        <html>
                <div id="main">
                        <div class="fof">
                                <h1>Unauthorized 401</h1>
                        </div>
                </div>


                <style>
                      *{
                        transition: all 0.6s;
                    }

                    html {
                        height: 100%;
                    }

                    body{
                        font-family: 'Lato', sans-serif;
                        color: #888;
                        margin: 0;
                    }

                    #main{
                        display: table;
                        width: 100%;
                        height: 100vh;
                        text-align: center;
                    }

                    .fof{
                          display: table-cell;
                          vertical-align: middle;
                    }

                    .fof h1{
                          font-size: 50px;
                          display: inline-block;
                          padding-right: 12px;
                          animation: type .5s alternate infinite;
                    }

                    @keyframes type{
                          from{box-shadow: inset -3px 0px 0px #888;}
                          to{box-shadow: inset -3px 0px 0px transparent;}
                    }
                </style>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=401)

