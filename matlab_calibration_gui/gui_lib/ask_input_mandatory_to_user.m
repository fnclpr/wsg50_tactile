function output = ask_input_mandatory_to_user(prompt, input_modifier)
%ASK_INPUT_TO_USER Summary of this function goes here
%   Detailed explanation goes here

if nargin < 2
    use_input_modifier = false;
else
    use_input_modifier = true;
end

output = [];
while isempty(output)
    if use_input_modifier
        output = input(prompt,input_modifier);
    else
        output = input(prompt);
    end
    if isempty(output)
        disp('Value is mandatory! ...');
    end
end

end

