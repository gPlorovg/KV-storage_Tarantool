box.watch('box.status', function()
    if box.info.ro then
        return
    end
    box.schema.create_space('data', {
        format = {
            { name = 'bucket_id', type = 'unsigned' },
            { name = 'key', type = 'string' },
            { name = 'value', type = 'any' }
        },
        if_not_exists = true
    })
    box.space.data:create_index('key', { parts = { 'key' }, unique = true, if_not_exists = true })
    box.space.data:create_index('bucket_id', { parts = { 'bucket_id' }, unique = false, if_not_exists = true })
end)
