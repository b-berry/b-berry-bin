#!/usr/bin/ruby

# Test bracket close string
char_map = {
    '{' => '}',
    '[' => ']',
    '(' => ')',
    '}' => '{',
    ']' => '[',
    ')' => '('
}

my_str_pass = '{[()]}'
my_str_fail = '{[(]}'
my_str_query = '(((([{()}[]]{{{[]}}}))))'

my_str_query.split('').each_with_index do |c,i|
    c_close = char_map.fetch(c)
    t = my_str_query.reverse[i]
    print c,c_close,t
    if c_close == t
        puts 'OK'
        next 
    else
        puts 'FAIL'
        break
    end
end 
