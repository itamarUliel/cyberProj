import colorama
from colorama import Fore
colorama.init(autoreset=True)

ERROR_COLOR = Fore.RED
OK_COLOR = Fore.GREEN
PENDING_COLOR = Fore.LIGHTBLUE_EX
DATA_COLOR = Fore.LIGHTYELLOW_EX


LOGO = Fore.LIGHTMAGENTA_EX + r"""                  
                   .:~!777!~^.           
                 ^7Y555YYY55P5J~         
                ~YYY7^:::::^7YPP?.       
          :~7?JJYYY5Y55555555?Y5P?!7^.   
        :J5PPYJJJJ7!!~~~~~~~!~~PP57PPY!  
       :YP5J: 755J            .!77:~5PP~ 
       !P55: .Y55~                  ?YY7 
       ~P55^ ^555:                   ..  
       .JPPY~!P5Y..........              
        .!J5Y755Y75555555YYYYYYYYYJ?!^.  
           .:7P5Y~!!!!!!!!!!!!!77?J5P5Y~ 
             ~P55:                 .?555:
       ~??7. ^555^                  :55P~
       !PP5: .YPP7             ...  ^555^
       .YPPJ~:7YYJ.           .Y55~~YPP? 
        .7Y5P55YYYJJJJJJJJJJJ775PY?P5J!  
           :^~!?YYYY??????77??5P5^^^:    
                7555?~^:::~7YP5J:        
                 :!JY555555YJ7^          
                    ..::::..                                                                                  
"""

FULL_LOGO = Fore.LIGHTMAGENTA_EX + r"""                                                                                                                                                      
                                                                                                                                                      
                                                                                                                                                      
                                                                                                                                                      
                                                                                                                                                      
                                                                      .:~~!!7!!~^:.                                                                   
                                                                   .~?Y5PPPPPPPPP5YJ!:                                                                
                                                                 .7YPPP5J?7777?JY5PPP5?.                                                              
                                                                :?YYJJ!:.       .^?555PY^                                                             
                                                          .:^~!7?JJJJJJJJJJYYYYJJJJ!Y55PY^~^.                                                         
                                                       :7JY5PPPPP555PPPPP5555555PPPJ!555P??PY?~.                                                      
                                                     .?5P5P5YJ????J!^^^^:::::::::^^^:JP5PY~5PPPY~                                                     
                                                    .JP555?^..?555Y.                 !YJJJ:~Y5555^                                                    
                                                    !P55P?   ^555P!                         ~555P?                                                    
                                                    ?5555~   7P555:                         .JYYY?                                                    
                                                    ?P555!  .J555Y.                                                                                   
                                                    ~5555Y: :555PJ                                                                                    
                                                     75P5557~5555?.::::::::::............                                                             
                                                      ^?55PY~555577P555555555555555555YYYYJ?7!^.                                                      
                                                        .^!7~555P?!YYYYYYYYYYYYYYYYYY5555PPPPP5Y7.                                                    
                                                            ^555PJ. ...................::^~?Y555PY.                                                   
                                                            :5555Y.                         .?555P7                                                   
                                                    ^^^^^.  .5555Y:                          ^555PJ.                                                  
                                                    JP5P5^  .J5555^                          :5555J.                                                  
                                                    7P555~   !P55P!                   ....   ~555P7                                                   
                                                    ^5555Y~. :Y555Y.                 ~5YY5^ ^Y55P5:                                                   
                                                     ~YP555Y?7?????~^^::::::::::::^^.?P555~Y5P5PY^                                                    
                                                      .!JY5PPPPP555555555555555555P?!555P7?P5YJ!.                                                     
                                                         .^~!7?JYJJYYYJJYYYYYJJJJJ?7555PJ:!~^.                                                        
                                                               .?YYYYJ~.        .~J555P?.                                                             
                                                                .75PPP5Y?7!!!!7JYPPP5J~                                                               
                                                                  .~?Y5PPPPPPPPP55Y7^                                                                 
                                                                     .:^~!!!!!!~^.                                                                    
                                                                                                                                                      
                                                                                                                                                      
                                                                                                                                                      
                                                                                                                                                      
        .:^~~~^:.           .~~.        :^^^^^^^^^^^^^  .^^^^^^^^^^^^^.              .:^^~~^^:.   :^.           ^:        .~~.    :~~~~~~~~~~~~~~~.   
     :7JJJ?777??JJ?^       .?55Y:       ?PJ??????????7  !PY??????????7.           .!?JJJ?777?J~  .J5:          .YJ.      .?55Y:   ^?77777YPJ777777.   
     JP~        .:!:      .?5~^5Y.      ?5^             !P!                      !5J~:           .J5:          .YJ.     .?5~^5Y:         ?5^          
     ^JY?7!~^^::.        .?5~  ^5Y.     ?5!^^^^^^^^^^^  !P?^^^^^^^^^^^.         !P7              .J5~^^^^^^^^^^~5J.    .?P~  ^5Y.        ?5^          
       :^!!7??JJJJ?~    .?5~ .. ^5J.    ?5J??????????7  !5Y???????????.         ?P~              .J5J???????????5J.   .?5~ .. ^5J.       ?5^          
      .         .:!P?  .?P5?JJJJ?YPJ.   ?5^             !P!                     :Y5~.            .J5:          .YJ.   ?P5?JJJJ?YPJ.      ?5^          
     .7J7~^::::^~!JY~ .?PJ~^:...:~?5J:  ?P^             !P?:^^^^^^^^^^           .!JY?!~^^^^~!?: .J5:          .YJ. .?PJ~^:...:~?5Y:     ?P^          
      .^!7??JJJ??7^.  ~J!          ^J7  !J^             ~JJJJJJJJJJJJ?.             :~!7????7!~.  7J:          .?7  ~J!          ^J7     !J:          
                                                                                                                                                      """

SMALL_FULL_LOGO = Fore.LIGHTMAGENTA_EX + r"""                                                                                                                   
                                                                                                                   
                                                                                                                   
                                                                                                                   
                                                    .^!??JJJJ?7~:                                                  
                                                  :7YPP5YJJJY5PP5J^                                                
                                                 :JYYJ~:.....:~J5P5!                                               
                                           .^!7?JYYYYYY5555555YJ?555!!!:                                           
                                         :?5PPPYYYYJ?7777777777?~JPPY?P5Y~                                         
                                        ^5P5Y!:~YY5~             ~YJJ^?55P!                                        
                                        JP55^  ?PPY.                  .YPPY.                                       
                                       .Y55Y. :Y5P7                    ^~~~.                                       
                                        ?P55! ^55P!                                                                
                                        .JPPP?!555~^~^^^^^^^^^^^^^:::..                                            
                                          ^?YJ7555!5PPPPPPPPPPPPPPPP55YJ7^                                         
                                             .!55P!:^^^^^^^^^^^^^~~!!?YPP5J.                                       
                                              ^55P7                   .755P7                                       
                                       .77?!  ^55P?                    .555J                                       
                                       .YPPY. .YP5Y.                   :55P?                                       
                                        !P557: 7555~             ~YJJ:.?555^                                       
                                         !YPP5YJJJJ?!!!!!!!!!!!7^?PPY75P5Y~                                        
                                          .^7?JY555555555555555J?555!??!^.                                         
                                                .?YYY?^:.....:!J5P5~                                               
                                                 .7YPP5J?77?JYPP5?:                                                
                                                   .^!?JYYYYY?7~.                                                  
                                                          .                                                        
                                                                                                                   
                                                                                                                   
      .:::::.         ::       .:::::::::. .:::::::::.            .::::.   ..         ..      ::    ::::::::::::   
    ~?777!77??!      ~55!     :YJ77777777: 7Y77777777~         ^7??7777?^  ?J        :Y^     ~YY7  .!7777YY7777!   
   .YJ:.     .:     ~5^:5!    :5~          ?Y                .JJ^.         ?J        :5^    ~5~:Y7       JJ        
    .~777?777!^    ~5^  :Y!   :5J7???????: ?5?7???7??!       !P:           ?5???????7?5^   ~5~  :Y7      JJ        
     .    ..:~JJ  ~PY7??7JP!  :5!........  ?Y.               :J?:          ?J........:5^  ^5Y7??7JP7     JJ        
    :??!~~~~!7?~ ~57^....:!5! :5!          ?5!!!!!!!!^        .~??7!!!!77. ?J        :5^ ~57^....:!57    JJ        
      .:^~~^^:   ^:        :^  ^.          :^~~^^^^~~^           .:^^^^:.  ::        .^. ^:        :^.   ::        
                                                                                                                   """
