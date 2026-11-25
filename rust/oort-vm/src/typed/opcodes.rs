//! Typed opcode numbers (spec 14).

pub(crate) const LOAD_K: u32 = 1;
pub(crate) const LOAD_L: u32 = 2;
pub(crate) const STORE_L: u32 = 3;
pub(crate) const LOAD_G: u32 = 4;
pub(crate) const DEF_FUN: u32 = 5;
pub(crate) const MOVE: u32 = 6;
pub(crate) const ADD_I: u32 = 10;
pub(crate) const ADD_F: u32 = 11;
pub(crate) const SUB_I: u32 = 12;
pub(crate) const SUB_F: u32 = 13;
pub(crate) const MUL_I: u32 = 14;
pub(crate) const MUL_F: u32 = 15;
pub(crate) const DIV_F: u32 = 16;
pub(crate) const FLOORDIV_I: u32 = 17;
pub(crate) const FLOORDIV_F: u32 = 18;
pub(crate) const MOD_I: u32 = 19;
pub(crate) const MOD_F: u32 = 20;
pub(crate) const EQ_I: u32 = 21;
pub(crate) const EQ_F: u32 = 22;
pub(crate) const EQ_B: u32 = 23;
pub(crate) const NE_I: u32 = 24;
pub(crate) const NE_F: u32 = 25;
pub(crate) const NE_B: u32 = 26;
pub(crate) const LT_I: u32 = 27;
pub(crate) const LT_F: u32 = 28;
pub(crate) const LE_I: u32 = 29;
pub(crate) const LE_F: u32 = 30;
pub(crate) const GT_I: u32 = 31;
pub(crate) const GT_F: u32 = 32;
pub(crate) const GE_I: u32 = 33;
pub(crate) const GE_F: u32 = 34;
pub(crate) const POS_I: u32 = 35;
pub(crate) const POS_F: u32 = 36;
pub(crate) const NEG_I: u32 = 37;
pub(crate) const NEG_F: u32 = 38;
pub(crate) const NOT_B: u32 = 39;
pub(crate) const TO_FLOAT: u32 = 40;
pub(crate) const JMP: u32 = 41;
pub(crate) const JMP_FALSE: u32 = 42;
pub(crate) const JMP_TRUE: u32 = 43;
pub(crate) const CALL: u32 = 44;
pub(crate) const RET: u32 = 45;
pub(crate) const EQ_MIXED: u32 = 46;
pub(crate) const NE_MIXED: u32 = 47;
pub(crate) const LT_MIXED: u32 = 48;
pub(crate) const LE_MIXED: u32 = 49;
pub(crate) const GT_MIXED: u32 = 50;
pub(crate) const GE_MIXED: u32 = 51;
pub(crate) const ADD_S: u32 = 52;
pub(crate) const EQ_S: u32 = 53;
pub(crate) const NE_S: u32 = 54;
pub(crate) const LT_S: u32 = 55;
pub(crate) const LE_S: u32 = 56;
pub(crate) const GT_S: u32 = 57;
pub(crate) const GE_S: u32 = 58;
pub(crate) const NEW_LIST: u32 = 59;
pub(crate) const NEW_TUPLE: u32 = 60;
pub(crate) const GET_ITEM: u32 = 61;
pub(crate) const EQ_LIST: u32 = 62;
pub(crate) const NE_LIST: u32 = 63;
pub(crate) const EQ_TUPLE: u32 = 64;
pub(crate) const NE_TUPLE: u32 = 65;
pub(crate) const OPEN_ITER: u32 = 66;
pub(crate) const ITER_NEXT: u32 = 67;
pub(crate) const SET_ITEM: u32 = 68;
pub(crate) const NEW_SET: u32 = 69;
pub(crate) const NEW_DICT: u32 = 70;
pub(crate) const EQ_SET: u32 = 71;
pub(crate) const NE_SET: u32 = 72;
pub(crate) const EQ_DICT: u32 = 73;
pub(crate) const NE_DICT: u32 = 74;
pub(crate) const NEW_ADT: u32 = 75;
pub(crate) const ADT_TAG: u32 = 76;
pub(crate) const ADT_FIELD: u32 = 77;
pub(crate) const EQ_ADT: u32 = 78;
pub(crate) const NE_ADT: u32 = 79;
pub(crate) const TUPLE_ITEM: u32 = 80;
pub(crate) const CONTAINS: u32 = 81;
pub(crate) const SLICE: u32 = 82;
pub(crate) const SET_UNION: u32 = 83;
pub(crate) const SET_INTERSECT: u32 = 84;
pub(crate) const SET_DIFFERENCE: u32 = 85;
pub(crate) const SET_SYMMETRIC: u32 = 86;
pub(crate) const MK_FUN: u32 = 87;
pub(crate) const MK_CLOSURE: u32 = 88;
pub(crate) const LOAD_OUTER: u32 = 89;
pub(crate) const STORE_OUTER: u32 = 90;
pub(crate) const FRESH_CELL: u32 = 91;
pub(crate) const SET_SUBSET: u32 = 92;
pub(crate) const SET_PROPER_SUBSET: u32 = 93;
pub(crate) const SET_SUPERSET: u32 = 94;
pub(crate) const SET_PROPER_SUPERSET: u32 = 95;
pub(crate) const CMP_LIST: u32 = 96;
pub(crate) const LIST_CONCAT: u32 = 97;

/// Human-readable opcode name for tracing and diagnostics.
pub(crate) fn name(op: u32) -> Option<&'static str> {
    Some(match op {
        LOAD_K => "LOAD_K",
        LOAD_L => "LOAD_L",
        STORE_L => "STORE_L",
        LOAD_G => "LOAD_G",
        DEF_FUN => "DEF_FUN",
        MOVE => "MOVE",
        ADD_I => "ADD_I",
        ADD_F => "ADD_F",
        SUB_I => "SUB_I",
        SUB_F => "SUB_F",
        MUL_I => "MUL_I",
        MUL_F => "MUL_F",
        DIV_F => "DIV_F",
        FLOORDIV_I => "FLOORDIV_I",
        FLOORDIV_F => "FLOORDIV_F",
        MOD_I => "MOD_I",
        MOD_F => "MOD_F",
        EQ_I => "EQ_I",
        EQ_F => "EQ_F",
        EQ_B => "EQ_B",
        NE_I => "NE_I",
        NE_F => "NE_F",
        NE_B => "NE_B",
        LT_I => "LT_I",
        LT_F => "LT_F",
        LE_I => "LE_I",
        LE_F => "LE_F",
        GT_I => "GT_I",
        GT_F => "GT_F",
        GE_I => "GE_I",
        GE_F => "GE_F",
        POS_I => "POS_I",
        POS_F => "POS_F",
        NEG_I => "NEG_I",
        NEG_F => "NEG_F",
        NOT_B => "NOT_B",
        TO_FLOAT => "TO_FLOAT",
        JMP => "JMP",
        JMP_FALSE => "JMP_FALSE",
        JMP_TRUE => "JMP_TRUE",
        CALL => "CALL",
        RET => "RET",
        EQ_MIXED => "EQ_MIXED",
        NE_MIXED => "NE_MIXED",
        LT_MIXED => "LT_MIXED",
        LE_MIXED => "LE_MIXED",
        GT_MIXED => "GT_MIXED",
        GE_MIXED => "GE_MIXED",
        ADD_S => "ADD_S",
        EQ_S => "EQ_S",
        NE_S => "NE_S",
        LT_S => "LT_S",
        LE_S => "LE_S",
        GT_S => "GT_S",
        GE_S => "GE_S",
        NEW_LIST => "NEW_LIST",
        NEW_TUPLE => "NEW_TUPLE",
        GET_ITEM => "GET_ITEM",
        EQ_LIST => "EQ_LIST",
        NE_LIST => "NE_LIST",
        EQ_TUPLE => "EQ_TUPLE",
        NE_TUPLE => "NE_TUPLE",
        OPEN_ITER => "OPEN_ITER",
        ITER_NEXT => "ITER_NEXT",
        SET_ITEM => "SET_ITEM",
        NEW_SET => "NEW_SET",
        NEW_DICT => "NEW_DICT",
        EQ_SET => "EQ_SET",
        NE_SET => "NE_SET",
        EQ_DICT => "EQ_DICT",
        NE_DICT => "NE_DICT",
        NEW_ADT => "NEW_ADT",
        ADT_TAG => "ADT_TAG",
        ADT_FIELD => "ADT_FIELD",
        EQ_ADT => "EQ_ADT",
        NE_ADT => "NE_ADT",
        TUPLE_ITEM => "TUPLE_ITEM",
        CONTAINS => "CONTAINS",
        SLICE => "SLICE",
        SET_UNION => "SET_UNION",
        SET_INTERSECT => "SET_INTERSECT",
        SET_DIFFERENCE => "SET_DIFFERENCE",
        SET_SYMMETRIC => "SET_SYMMETRIC",
        MK_FUN => "MK_FUN",
        MK_CLOSURE => "MK_CLOSURE",
        LOAD_OUTER => "LOAD_OUTER",
        STORE_OUTER => "STORE_OUTER",
        FRESH_CELL => "FRESH_CELL",
        SET_SUBSET => "SET_SUBSET",
        SET_PROPER_SUBSET => "SET_PROPER_SUBSET",
        SET_SUPERSET => "SET_SUPERSET",
        SET_PROPER_SUPERSET => "SET_PROPER_SUPERSET",
        CMP_LIST => "CMP_LIST",
        LIST_CONCAT => "LIST_CONCAT",
        _ => return None,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn opcode_names_cover_the_typed_set() {
        assert_eq!(name(LOAD_K), Some("LOAD_K"));
        assert_eq!(name(ADD_I), Some("ADD_I"));
        assert_eq!(name(LIST_CONCAT), Some("LIST_CONCAT"));
        assert_eq!(name(0), None);
        assert_eq!(name(255), None);
    }
}
