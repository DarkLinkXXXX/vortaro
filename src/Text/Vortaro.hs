import qualified Data.Set as S

data Definition = Definition { wordLeft :: String
                             , wordRight :: String
                             , partOfSpeech :: String }
data Dictionary = Dictionary { source :: String
                             , langLeft :: Language
                             , langRight :: Language
                             , definitions :: [Definition] }

-- https://stackoverflow.com/a/30588782
substring :: String -> String -> Bool
substring (x:xs) [] = False
substring xs ys
    | prefix xs ys = True
    | substring xs (tail ys) = True
    | otherwise = False
prefix :: String -> String -> Bool
prefix [] ys = True
prefix (x:xs) [] = False
prefix (x:xs) (y:ys) = (x == y) && prefix xs ys

fromString :: String -> Maybe Dictionary
fromString
  | (substring "vocabulary database	compiled by dict.cc" firstLine) = Just . dictcc
  | (substring "CC-CEDICT" firstLine) = Just . cedict
  | (substring "ESPDIC" firstLine) = Just . espdic
  | otherwise = Nothing
  where
    firstLine = head $ lines x

{-
Sample first lines:
# SR-EN vocabulary database	compiled by dict.cc
# EN-SR vocabulary database	compiled by dict.cc
# FR-EN vocabulary database	compiled by dict.cc

e
-}
dictcc :: String -> Dictionary
dictcc text
  where
    firstLine = head $ lines x
