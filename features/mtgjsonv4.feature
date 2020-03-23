Feature: Outputting Sets
    Scenario Outline: Output a set
        Given we build a v4 argument
        And we install mtgjson
        When we build a <set_code> argument
        When we include the skip-keys argument
        When we run the cli
        Then we will render the set to <set_json_file>
    Examples: Sets
        | set_code   | set_json_file |
        | 4ed        | 4ED           |
