package = 'crud'
version = '1.5.2-1'
source  = {
    url = 'git+https://github.com/tarantool/crud.git',
    tag = '1.5.2',
}

description = {
    license = 'BSD',
}

dependencies = {
    'lua ~> 5.1',
    'checks >= 3.1.0-1',
    'errors >= 2.2.1-1',
    'vshard >= 0.1.18-1',
}

build = {
    type = 'cmake',
    variables = {
        version = '1.5.2-1',
        TARANTOOL_INSTALL_LUADIR = '$(LUADIR)',
    },
}
