function output = ask_input_with_default_to_user(prompt, default_value, input_modifier)
%ASK_INPUT_TO_USER Summary of this function goes here
%   Detailed explanation goes here

if nargin < 3
    use_input_modifier = false;
else
    use_input_modifier = true;
end

prompt = [prompt '(' num2str(default_value) ') '];
if use_input_modifier
    output = input(prompt,input_modifier);
else
    output = input(prompt);
end

if isempty(output)
    output = default_value;
end

end

