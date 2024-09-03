box.watch('box.status', function()
    if box.info.ro then
        return
    end

    box.schema.create_space('tokens', {
        format = {
            { name = 'bucket_id', type = 'unsigned' },
            { name = 'login', type = 'string' },
            { name = 'token', type = 'string' }
        },
        if_not_exists = true
    })
    box.space.tokens:create_index('login', { parts = { 'login' }, unique = true, if_not_exists = true })
    box.space.tokens:create_index('bucket_id', { parts = { 'bucket_id' }, unique = false, if_not_exists = true })

    box.schema.create_space('users', {
        format = {
            { name = 'bucket_id', type = 'unsigned' },
            { name = 'login', type = 'string' },
            { name = 'password', type = 'string' }
        },
        if_not_exists = true
    })
    box.space.users:create_index('login', { parts = { 'login' }, unique = true, if_not_exists = true })
    box.space.users:create_index('bucket_id', { parts = { 'bucket_id' }, unique = false, if_not_exists = true })
end)
