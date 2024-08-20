box.cfg{
    listen = 3301,
    log_level = 5,
}

local function bootstrap()
    local space = box.schema.space.create('data', {if_not_exists = true})
    space:format({
        {name = 'id', type = 'unsigned'},
        {name = 'value', type = 'string'},
    })
    space:create_index('primary', {
        type = 'tree',
        parts = {'id'},
        if_not_exists = true,
    })
end

box.once('bootstrap', bootstrap)
